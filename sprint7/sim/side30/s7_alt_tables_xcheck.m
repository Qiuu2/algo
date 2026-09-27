function s7_alt_tables_xcheck()
% s7_alt_tables_xcheck.m -- S7-SIDE30, iron rule 7 second tool (MATLAB) for gen_m2_wtbl.py / s7_alt_tables.py.
%  (1) re-derives RS-A / RS-B from their definition (gen_m2_wtbl.py RS block) with MATLAB integral() --
%      adaptive quadrature, a third method next to Gauss-Legendre and the Jacobi-Anger series -- plus backslash,
%      and checks the Q15 rows are identical to sel 4 / sel 5 in m2_wtbl_q15.h;
%  (2) recomputes, for the frozen D20 and every Q15 row of the header, the 8 JY/T single-frequency points, the
%      7-band R90 band averages (31 log-spaced points per 1/3 octave), BW(-6 dB full)@1k by fzero, and the
%      on-axis level vs D20, and compares them with s7_alt_tables_ideal.csv (written by numpy, 3 decimals).
% [L2 cross-check of an L2 model; nothing here is measured]. Output: s7_alt_tables_xcheck.log next to this file.
here = fileparts(mfilename('fullpath'));
repo = fullfile(here, '..', '..', '..');
fid = fopen(fullfile(here, 's7_alt_tables_xcheck.log'), 'w');
out = @(varargin) fprintf_both(fid, varargin{:});
out('s7_alt_tables_xcheck.m  MATLAB %s  [L2 cross-check]\n', version);

c = 343.0; d = 0.055; X = ((0:15) - 7.5) * d; xc = X(1:8);
hdr = fileread(fullfile(repo, 'sprint6', 'dsp', 'audio', 'm1_cces_project', 'src', 'm2_wtbl_q15.h'));
tok = regexp(hdr, '\{\s*([\d,\s]+?)\s*\},\s*/\* sel (\d+): (\S+ \S+)', 'tokens');
frz = fileread(fullfile(repo, 'sprint4', 'dsp', 'fira', 'dolph_w8_q15.h'));
blk = frz(strfind(frz, 'g_dolph_w8_q15[DOLPH_W8_NCH] = {'):end);
i1 = strfind(blk, '{'); i2 = strfind(blk, '};');
blk = blk(i1(1) + 1:i2(1) - 1);
d20 = cellfun(@str2double, regexp(blk, '(?m)^\s*(\d+),', 'tokens', 'lineanchors'));
names = {'D20q'}; Q = {d20};
labs = {'D25q', 'D30q', 'D35q', 'RS-Aq', 'RS-Bq'};
for i = 1:numel(tok)
    names{end + 1} = labs{i}; %#ok<AGROW>
    Q{end + 1} = str2double(strsplit(strtrim(tok{i}{1}), ',')); %#ok<AGROW>
end
out('parsed frozen D20 %s and %d header rows\n', mat2str(d20), numel(tok));

% ---- (1) RS rows from the definition ------------------------------------------------------------------------
bands = [1000 1250 1600 2000 2500 3150 4000];
F7 = [];
for fc = bands
    F7 = [F7, logspace(log10(fc * 2^(-1/6)), log10(fc * 2^(1/6)), 31)]; %#ok<AGROW>
end
p0 = deg2rad(5);
sg = integral(@(a) 10.^(a / 10), -1, 1) / 2 - 2 * (integral(@(a) 10.^(a / 20), -1, 1) / 2) * ...
     (integral(@cos, -p0, p0) / (2 * p0)) + 1;
sx2 = (0.5e-3)^2 / 3;
out('sigma_g^2 (MATLAB integral) = %.12f\n', sg);
specs = {'RS-A', 60, 35, 0.1, 5; 'RS-B', 60, 30, 1.0, 6};
allok = true;
for s = 1:2
    ths = specs{s, 2}; thm = specs{s, 3}; eta = specs{s, 4};
    Qm = zeros(8);
    for f = F7
        k = 2 * pi * f / c;
        Qm = Qm + rmean(ths, 90, k, xc) + eta * rmean(thm, ths, k, xc) + 2 * (sg + k^2 * sx2) * eye(8);
    end
    W = (Qm / numel(F7)) \ ones(8, 1);
    w = W' / max(W);
    q = round(w * 32768);
    ok = isequal(q, Q{specs{s, 5}});
    allok = allok && ok;
    out('%s: MATLAB Q15 %s vs header %s -> %s ; min distance to a rounding tie %.4f LSB\n', specs{s, 1}, ...
        mat2str(q), mat2str(Q{specs{s, 5}}), pass(ok), min(abs(w * 32768 - floor(w * 32768) - 0.5)));
end

% ---- (2) metrics vs the numpy CSV -----------------------------------------------------------------------------
T = readtable(fullfile(here, 's7_alt_tables_ideal.csv'), 'TextType', 'string', 'Delimiter', ',');
jyt = [30 500; 90 500; 30 1000; 90 1000; 30 2000; 90 2000; 30 4000; 90 4000];
maxd = 0; maxbw = 0; nchk = 0;
for i = 1:numel(names)
    w8 = Q{i} / 32768; w16 = [w8, fliplr(w8)];
    for j = 1:size(jyt, 1)
        v = att(jyt(j, 1), jyt(j, 2), w16, X, c);
        ref = pick(T, names{i}, sprintf('JYT_%d_%d_single', jyt(j, 2), jyt(j, 1)), jyt(j, 2));
        maxd = max(maxd, abs(v - ref)); nchk = nchk + 1;
    end
    for fc = bands
        fs = logspace(log10(fc * 2^(-1/6)), log10(fc * 2^(1/6)), 31);
        p0s = 0; p9s = 0;
        for f = fs
            p0s = p0s + abs(af(0, f, w16, X, c))^2; p9s = p9s + abs(af(90, f, w16, X, c))^2;
        end
        v = 10 * log10(p0s / p9s);
        ref = pick(T, names{i}, 'R90_band', fc);
        maxd = max(maxd, abs(v - ref)); nchk = nchk + 1;
    end
    g = @(th) 20 * log10(abs(af(th, 1000, w16, X, c)) / abs(af(0, 1000, w16, X, c))) + 6;
    bw = 2 * fzero(g, [1e-6, 60]);
    maxbw = max(maxbw, abs(bw - pick(T, names{i}, 'BW_1k_deg', 1000)));
    ax = 20 * log10(sum(w8) / sum(d20 / 32768));
    maxd = max(maxd, abs(ax - pick(T, names{i}, 'onaxis_vs_D20_dB', 0))); nchk = nchk + 2;
    out('  %-6s BW1k %.3f deg  on-axis %+.3f dB  1k/30 %.3f  500/30 %.3f dB\n', names{i}, bw, ax, ...
        att(30, 1000, w16, X, c), att(30, 500, w16, X, c));
end
okm = maxd <= 1.5e-3 && maxbw <= 2e-3;
allok = allok && okm;
out('metrics: %d values (8 JY/T + 7 R90 + BW1k + on-axis per table, %d tables) max|MATLAB - numpy CSV| = %.2e dB; BW1k max diff %.2e deg -> %s\n', ...
    nchk, numel(names), maxd, maxbw, pass(okm));
out('(tolerances 1.5e-3 dB / 2e-3 deg = CSV 3-decimal rounding + numpy BW grid interpolation)\n');
out('OVERALL %s\n', pass(allok));
fclose(fid);
end

function R = rmean(t1, t2, k, xc)
t1 = deg2rad(t1); t2 = deg2rad(t2);
R = integral(@(th) (2 * cos(k * xc' * sin(th))) * (2 * cos(k * xc * sin(th))), t1, t2, ...
             'ArrayValued', true, 'AbsTol', 1e-14, 'RelTol', 1e-12) / (t2 - t1);
end

function a = af(th, f, w16, X, c)
a = sum(w16 .* exp(1i * 2 * pi * f / c * sind(th) * X));
end

function v = att(th, f, w16, X, c)
v = -20 * log10(abs(af(th, f, w16, X, c)) / abs(af(0, f, w16, X, c)));
end

function v = pick(T, name, metric, f)
r = T(T.design == name & T.metric == metric & T.freq_hz == f, :);
assert(height(r) == 1, 'CSV lookup %s %s %g', name, metric, f);
v = r.value;
end

function s = pass(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end

function fprintf_both(fid, varargin)
fprintf(varargin{:});
fprintf(fid, varargin{:});
end
