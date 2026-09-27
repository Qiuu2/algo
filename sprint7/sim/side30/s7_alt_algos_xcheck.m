function s7_alt_algos_xcheck()
% s7_alt_algos_xcheck.m -- S7-SIDE30, iron rule 7 second tool (MATLAB) for s7_alt_algos.py.
%  (1) re-derives the representative crossover design X3-LR4-700/1600-e0.1m35 from its definition (band 1 = frozen D20;
%      bands 2/3 minimise mean_f W'QW over the 7 bands, Q = R(60-90) + 0.1 R(35-60) + 2(sg + k^2 sx2) I with the same
%      0.25-deg sector rule as s7_fir_robust_design.sector_cov; constraints sum 2w = 1 per band) with its own LR
%      magnitudes and KKT solve, and compares the band gains with s7_alt_algos_params.csv;
%  (2) re-derives Keele 2002 eqs (3)-(7) (Legendre shading, arc radius, delays) for arc 20 deg and compares;
%  (3) recomputes R90 (7 bands, 31 log points), the 8 JY/T single-frequency points and BW(-6)@1k for
%      X3-LR4-700/1600-e0.1m35, CBT-arc20, Legendre-only and DDC-BW30 and compares with s7_alt_algos_ideal.csv.
% [L2 cross-check; nothing measured]. Output: s7_alt_algos_xcheck.log next to this file.
here = fileparts(mfilename('fullpath'));
repo = fullfile(here, '..', '..', '..');
fid = fopen(fullfile(here, 's7_alt_algos_xcheck.log'), 'w');
out = @(varargin) fprintf_both(fid, varargin{:});
out('s7_alt_algos_xcheck.m  MATLAB %s  [L2 cross-check]\n', version);
c = 343.0; d = 0.055; X = ((0:15) - 7.5) * d; xc = X(1:8); fsamp = 48000;
po = detectImportOptions(fullfile(here, 's7_alt_algos_params.csv'));
po = setvartype(po, {'design', 'order_or_kind', 'xo_hz_or_arc_deg', 'band_or_param'}, 'string');
P = readtable(fullfile(here, 's7_alt_algos_params.csv'), po);
T = readtable(fullfile(here, 's7_alt_algos_ideal.csv'), 'TextType', 'string', 'Delimiter', ',');
cols = {'c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7'};
getrow = @(name, key) table2array(P(P.design == name & P.band_or_param == key, cols));
allok = true;

% ---- (1) crossover design re-derivation ------------------------------------------------------------------------------
Tw = readtable(fullfile(repo, 'sprint4', 'dsp', 'fira', 'dolph_w8_q15.csv'));   % quoted "{c,15-c}" field -> readtable
d20 = zeros(1, 8); d20(Tw.ch + 1) = Tw.w_float_track1_scipy;
d20n = d20 / (2 * sum(d20));
bands = [1000 1250 1600 2000 2500 3150 4000];
F7 = [];
for fc = bands
    F7 = [F7, logspace(log10(fc * 2^(-1/6)), log10(fc * 2^(1/6)), 31)]; %#ok<AGROW>
end
p0 = deg2rad(5);
sg = integral(@(a) 10.^(a / 10), -1, 1) / 2 - 2 * (integral(@(a) 10.^(a / 20), -1, 1) / 2) * ...
     (integral(@cos, -p0, p0) / (2 * p0)) + 1;
sx2 = (0.5e-3)^2 / 3;
xo = [700 1600]; ord = 4;
H = zeros(16); g = zeros(16, 1);
for f = F7
    k = 2 * pi * f / c;
    Q = seccov(60, 90, k, xc) + 0.1 * seccov(35, 60, k, xc) + 2 * (sg + k^2 * sx2) * eye(8);
    m = lrm(f, xo, ord, fsamp);
    mf = m(2:3)'; H = H + kron(mf * mf', Q) / numel(F7); g = g + kron(mf, Q * (m(1) * d20n')) / numel(F7);
end
C = kron(eye(2), 2 * ones(1, 8));
x = [H, C'; C, zeros(2)] \ [-g; ones(2, 1)];
wk_m = [d20n; reshape(x(1:16), 8, 2)'];
name = "X3-LR4-700/1600-e0.1m35";
wk_p = [getrow(name, "1"); getrow(name, "2"); getrow(name, "3")];
dw = max(abs(wk_m(:) - wk_p(:))) / max(abs(wk_p(:)));
ok1 = dw < 1e-8; allok = allok && ok1;
out('(1) %s band gains: max relative |MATLAB - numpy| = %.2e -> %s\n', name, dw, pass(ok1));

% ---- (2) Keele 2002 eqs (3)-(7), arc 20 deg ------------------------------------------------------------------------------
HT = 16 * d; R = HT / (2 * sin(deg2rad(20) / 2)); h = abs(xc);
tau = R * (1 - cos(asin(h / R))) / c * 1e6;
xx = h / (HT / 2); U = (1 + 0.066 * xx - 1.8 * xx.^2 + 0.743 * xx.^3) .* (xx <= 1);
dU = max(abs(U - getrow("CBT-arc20", "U"))); dT = max(abs(tau - getrow("CBT-arc20", "tau_us")));
ok2 = dU < 1e-10 && dT < 1e-7; allok = allok && ok2;
out('(2) CBT-arc20: U max diff %.1e, tau max diff %.1e us (max tau %.2f us) -> %s\n', dU, dT, max(tau), pass(ok2));

% ---- (3) metrics -------------------------------------------------------------------------------------------------------------
jyt = [30 500; 90 500; 30 1000; 90 1000; 30 2000; 90 2000; 30 4000; 90 4000];
designs = {name, "CBT-arc20", "Legendre-only", "DDC-BW30"};
maxd = 0; maxbw = 0; n = 0;
for i = 1:numel(designs)
    nm = designs{i};
    A = respfun(nm, wk_p, xo, ord, fsamp, getrow, xc, c);
    for fc = bands
        fs = logspace(log10(fc * 2^(-1/6)), log10(fc * 2^(1/6)), 31);
        p = [0 0];
        for f = fs
            p = p + abs(afp(A(f), f, [0 90], xc, c)).^2;
        end
        v = 10 * log10(p(1) / p(2));
        maxd = max(maxd, abs(v - pick(T, nm, 'R90_band', fc))); n = n + 1;
    end
    for j = 1:size(jyt, 1)
        a = afp(A(jyt(j, 2)), jyt(j, 2), [0 jyt(j, 1)], xc, c);
        v = -20 * log10(abs(a(2)) / abs(a(1)));
        maxd = max(maxd, abs(v - pick(T, nm, sprintf('JYT_%d_%d_single', jyt(j, 2), jyt(j, 1)), jyt(j, 2)))); n = n + 1;
    end
    gfun = @(th) 20 * log10(abs(afp(A(1000), 1000, th, xc, c)) / abs(afp(A(1000), 1000, 0, xc, c))) + 6;
    bw = 2 * fzero(gfun, [1e-6, 80]);
    maxbw = max(maxbw, abs(bw - pick(T, nm, 'BW_1k_deg', 1000)));
    out('  %-26s BW1k %.3f deg (numpy %.3f)\n', nm, bw, pick(T, nm, 'BW_1k_deg', 1000));
end
ok3 = maxd <= 1.5e-3 && maxbw <= 2e-3; allok = allok && ok3;
out('(3) %d values (7 R90 + 8 JY/T per design, %d designs): max|MATLAB - numpy CSV| = %.2e dB; BW1k max diff %.2e deg -> %s\n', ...
    n, numel(designs), maxd, maxbw, pass(ok3));
out('(tolerances 1.5e-3 dB / 2e-3 deg = CSV 3-decimal rounding + numpy BW grid interpolation)\n');
out('OVERALL %s\n', pass(allok));
fclose(fid);
end

function R = seccov(t1, t2, k, xc)
th = deg2rad(t1:0.25:t2 + 1e-9);          % same rule as sector_cov: equally spaced, both ends, plain mean
a = 2 * cos(k * sin(th)' * xc);
R = (a' * a) / numel(th);
end

function m = lrm(f, xo, ord, fsamp)
t = @(fc) (tan(pi * min(f, fsamp / 2 - 1) / fsamp) / tan(pi * fc / fsamp))^ord;
lp1 = 1 / (1 + t(xo(1))); hp1 = t(xo(1)) / (1 + t(xo(1)));
lp2 = 1 / (1 + t(xo(2))); hp2 = t(xo(2)) / (1 + t(xo(2)));
m = [lp2 * lp1, lp2 * hp1, hp2];
end

function A = respfun(nm, wk, xo, ord, fsamp, getrow, xc, c)
if startsWith(nm, "X3")
    A = @(f) lrm(f, xo, ord, fsamp) * wk;
elseif nm == "DDC-BW30"
    A = @(f) ddc(f, xc, c);
else
    U = getrow(nm, "U"); tau = getrow(nm, "tau_us") * 1e-6;
    A = @(f) U .* exp(-1i * 2 * pi * f * tau) / (2 * sum(U));
end
end

function w = ddc(f, xc, c)
a = min(max((69 / 30) * (c / f) / 2, 0.6 * 0.055), 16 * 0.055 / 2);
u = abs(xc) / a; w = (u < 1) .* cos(pi / 2 * u).^2; w = w / (2 * sum(w));
end

function a = afp(A, f, th, xc, c)
a = zeros(1, numel(th));
for i = 1:numel(th)
    a(i) = sum(A .* 2 .* cos(2 * pi * f / c * xc * sind(th(i))));
end
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
