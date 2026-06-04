% PREREQUISITE #2 v1 on-axis focusing/depth-zoning efficacy sim -- MATLAB INDEPENDENT TRACK.
% 铁律七 dual-track: independent re-implementation of the SAME spherical-wave equation,
% NOT a call into the numpy result. Weights re-read independently from the frozen CSV.
% Outputs results_matlab.json for quantitative comparison vs results_numpy.json.
% L-grade: sim field = [L2/仿真]; feasibility = [L3/解析]; no L1 in scope.

function focus_sim_matlab()
    C = 343.0;                       % m/s (20 C)
    N = 16;
    d = 0.055;                       % m
    Laper = (N-1)*d;                 % 0.825 m aperture
    xn = ((0:N-1) - (N-1)/2) * d;    % centered element positions

    here = fileparts(mfilename('fullpath'));
    repo = fileparts(fileparts(here));
    w8csv = fullfile(repo, 'sprint4', 'dsp', 'fira', 'dolph_w8_q15.csv');

    % --- independently read the 8 float channel weights (scipy track-1 col) ---
    w8 = read_w8(w8csv);             % column 'w_float_track1_scipy'
    w16 = [w8, fliplr(w8)];          % symmetric expansion [w0..w7 w7..w0]
    assert(numel(unique(round(w8,12)))==8, 'FG1: weights not all distinct');
    assert(max(abs(w16 - fliplr(w16)))==0, 'symmetric expansion broken');

    freqs  = [500 1000 2000 4000 6000];
    focals = [2 3 5 8 12];
    zonePairs = [3 8; 2 5];

    % ---------------- ANCHORS ----------------
    ang = -90:0.01:90;
    Pff = farfield_db(ang, 1000.0, w16, xn, C);
    bw1k = bw_neg6_full(Pff, ang);
    sll  = peak_sll_db(Pff, ang);
    % A2 8-pair equivalence (built symmetric => exact)
    tau16 = focus_delays(3.0, xn, C);
    tau8  = tau16(1:8); tau16b = [tau8, fliplr(tau8)];
    yy = linspace(-0.5,0.5,41); zz = linspace(1,6,51);
    [Y,Z] = ndgrid(yy,zz);
    pi_  = press_field(Y,Z,2000.0,w16,tau16,xn,C);
    pii_ = press_field(Y,Z,2000.0,w16,tau16b,xn,C);
    a2diff = max(abs(pi_(:)-pii_(:)));
    fprintf('MATLAB anchors: BW@1k=%.4f deg  SLL=%.4f dB  A2diff=%.3e\n', bw1k, sll, a2diff);
    if abs(bw1k-29.269) > 0.1, error('A1 FAIL %.4f', bw1k); end
    if abs(sll+20.0)    > 0.1, error('A3 FAIL %.4f', sll);  end
    if a2diff > 1e-9,          error('A2 FAIL %.3e', a2diff); end

    % ---------------- METRICS ----------------
    R = struct();
    R.anchors = struct('A1_farfield_BW_1k_deg', bw1k, 'A3_peak_SLL_dB', sll, ...
                       'A2_paired_vs_16elem_max_abs_diff', a2diff);
    R.freqs = freqs; R.focals = focals;
    cells = struct();
    for fi = 1:numel(freqs)
        f = freqs(fi); fk = sprintf('f%d', f);
        for Fi = 1:numel(focals)
            F = focals(Fi); Fk = sprintf('F%d', F);
            % focal gain
            tauF = focus_delays(F, xn, C);
            tau0 = zeros(1,N);
            pF = press_field(0.0, F, f, w16, tauF, xn, C);
            pB = press_field(0.0, F, f, w16, tau0, xn, C);
            fg = 20*log10(abs(pF)) - 20*log10(abs(pB));
            % axial depth
            [depth] = axial_depth(F, f, w16, xn, C);
            % lateral width
            lw = lateral_w(F, f, w16, xn, C);
            cells.(fk).(Fk) = struct('focal_gain_dB', fg, ...
                'axial_zone_depth_m', depth, 'lateral_width_m', lw);
        end
    end
    R.per_cell = cells;
    % cross-zone isolation
    cz = struct();
    for zp = 1:size(zonePairs,1)
        z1 = zonePairs(zp,1); z2 = zonePairs(zp,2);
        pk = sprintf('p%d_%d', z1, z2);
        spread = 20*log10(z2/z1);
        for fi = 1:numel(freqs)
            f = freqs(fi); fk = sprintf('f%d', f);
            tau1 = focus_delays(z1, xn, C); tau2 = focus_delays(z2, xn, C);
            S = @(tau,zm) 20*log10(abs(press_field(0.0, zm, f, w16, tau, xn, C)));
            f1m1 = S(tau1,z1); f1m2 = S(tau1,z2);
            f2m1 = S(tau2,z1); f2m2 = S(tau2,z2);
            iso1 = f1m1 - f1m2; iso2 = f2m2 - f2m1;
            cz.(pk).(fk) = struct('isolation_z1_on_minus_off_dB', iso1, ...
                'isolation_z2_on_minus_off_dB', iso2, ...
                'geometric_spreading_dB', spread, ...
                'focusing_excess_z1_dB', iso1-spread, ...
                'focusing_excess_z2_dB', iso2+spread, ...
                'focus_z1_meas_z1_dB', f1m1, 'focus_z1_meas_z2_dB', f1m2, ...
                'focus_z2_meas_z1_dB', f2m1, 'focus_z2_meas_z2_dB', f2m2);
        end
    end
    R.cross_zone = cz;

    out = fullfile(here, 'results_matlab.json');
    fid = fopen(out, 'w'); fprintf(fid, '%s', jsonencode(R)); fclose(fid);
    fprintf('WROTE %s\n', out);
end

% ---------- model functions (independent implementation) ----------
function tau = focus_delays(F, xn, C)
    r = sqrt(xn.^2 + F^2);
    tau = (r - min(r)) / C;
end

function p = press_field(Y, Z, f, w16, tau, xn, C)
    k = 2*pi*f / C;
    Y = double(Y); Z = double(Z);
    p = zeros(size(Y+Z));
    for n = 1:numel(xn)
        rn = sqrt((Y - xn(n)).^2 + Z.^2);
        rn = max(rn, 1e-9);
        p = p + w16(n) ./ (4*pi*rn) .* exp(-1j*k*(rn - C*tau(n)));
    end
end

function P = farfield_db(ang, f, w16, xn, C)
    k = 2*pi*f/C;
    st = sin(deg2rad(ang));
    % (n_theta x N)
    phase = k * (st(:) * xn);
    af = abs(sum(w16 .* exp(1j*phase), 2));
    P = 20*log10(af / max(af) + 1e-12).';
end

function bw = bw_neg6_full(P, ang)
    [~, i0] = max(P);
    iR = i0; while iR < numel(P) && P(iR) > -6, iR = iR+1; end
    iL = i0; while iL > 1 && P(iL) > -6, iL = iL-1; end
    if iR >= numel(P) || iL <= 1, bw = 180.0; return; end
    aR = interp1([P(iR) P(iR-1)], [ang(iR) ang(iR-1)], -6);
    aL = interp1([P(iL) P(iL+1)], [ang(iL) ang(iL+1)], -6);
    bw = aR - aL;
end

function sll = peak_sll_db(P, ang)
    [~, i0] = max(P);
    iR = i0; while iR < numel(P) && P(iR+1) <= P(iR), iR = iR+1; end
    iL = i0; while iL > 2 && P(iL-1) <= P(iL), iL = iL-1; end
    mask = true(1, numel(P)); mask(iL:iR) = false;
    if ~any(mask), sll = -60.0; return; end
    sll = max(P(mask));
end

function depth = axial_depth(F, f, w16, xn, C)
    tau = focus_delays(F, xn, C);
    z_lo = max(0.2, F*0.1); z_hi = F*6.0 + 20.0;
    z = linspace(z_lo, z_hi, 60001);
    p = press_field(zeros(size(z)), z, f, w16, tau, xn, C);
    db = 20*log10(abs(p) + 1e-300);
    [pk, ipk] = max(db); thr = pk - 6.0;
    iL = ipk; while iL > 1 && db(iL) > thr, iL = iL-1; end
    if db(iL) > thr, znear = z(1); else
        znear = interp1([db(iL) db(iL+1)], [z(iL) z(iL+1)], thr); end
    iR = ipk; while iR < numel(db) && db(iR) > thr, iR = iR+1; end
    if db(iR) > thr, zfar = z(end); else
        zfar = interp1([db(iR-1) db(iR)], [z(iR-1) z(iR)], thr); end
    depth = zfar - znear;
end

function lw = lateral_w(F, f, w16, xn, C)
    tau = focus_delays(F, xn, C);
    y = linspace(-F, F, 40001);
    p = press_field(y, F*ones(size(y)), f, w16, tau, xn, C);
    db = 20*log10(abs(p) + 1e-300);
    [pk, ipk] = max(db); thr = pk - 6.0;
    iR = ipk; while iR < numel(db) && db(iR) > thr, iR = iR+1; end
    if db(iR) > thr, yR = y(end); else
        yR = interp1([db(iR-1) db(iR)], [y(iR-1) y(iR)], thr); end
    iL = ipk; while iL > 1 && db(iL) > thr, iL = iL-1; end
    if db(iL) > thr, yL = y(1); else
        yL = interp1([db(iL) db(iL+1)], [y(iL) y(iL+1)], thr); end
    lw = yR - yL;
end

function w8 = read_w8(path)
    T = readtable(path, 'TextType', 'string');
    w8 = zeros(1,8);
    for i = 1:height(T)
        c = T.ch(i);
        w8(c+1) = T.w_float_track1_scipy(i);
    end
end
