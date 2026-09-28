function s7_hybrid_lpxo_xcheck()
% s7_hybrid_lpxo_xcheck.m -- S7-SIDE30, iron rule 7 second tool (MATLAB) for s7_hybrid_lpxo.py.
%  (1) from the stored low-pass taps (s7_hybrid_lpxo_params.csv): symmetry (a real check) and, with the CSV band
%      gains, the on-axis identity sum_c 2 h_c == delta[n-D] (a real check of gains + bank). Perfect reconstruction
%      (sum of bands == delta) is printed but is a CONSTRUCTION IDENTITY (the bands telescope) -- critic R3g F4;
%  (2) re-derives the LPX3-b band gains (band 1 = frozen D20; KKT with the same 0.25-deg sector rule and load) and
%      compares them with the CSV;
%  (3) recomputes R90 (7 bands + 5 kHz, 31 log points) and the 8 JY/T single-frequency points for LPX3-b and
%      LPX4-b-cap from the CSV gains and compares with s7_hybrid_lpxo_ideal.csv;
%  (4) recomputes LPX3-b's per-channel peaks for full-scale squares (100 Hz / 1 kHz / 3 kHz, from silence) and the
%      L1 bound with MATLAB filter(), and compares with s7_hybrid_lpxo_headroom.csv.
% [L2 cross-check; nothing measured]. Output: s7_hybrid_lpxo_xcheck.log next to this file.
here = fileparts(mfilename('fullpath'));
repo = fullfile(here, '..', '..', '..');
fid = fopen(fullfile(here, 's7_hybrid_lpxo_xcheck.log'), 'w');
out = @(varargin) fprintf_both(fid, varargin{:});
out('s7_hybrid_lpxo_xcheck.m  MATLAB %s  [L2 cross-check]\n', version);
c = 343.0; d = 0.055; xc = (((0:15) - 7.5) * d); xc = xc(1:8); fs = 48000;
txt = fileread(fullfile(here, 's7_hybrid_lpxo_params.csv'));
L = splitlines(strtrim(txt)); L = L(2:end);
P = struct('design', {}, 'item', {}, 'vals', {});
for i = 1:numel(L)
    v = strsplit(L{i}, ',', 'CollapseDelimiters', false);
    P(end + 1) = struct('design', v{1}, 'item', v{2}, 'vals', str2double(v(5:end))); %#ok<AGROW>
end
getp = @(dsg, item) P(strcmp({P.design}, dsg) & strcmp({P.item}, item)).vals;
Tw = readtable(fullfile(repo, 'sprint4', 'dsp', 'fira', 'dolph_w8_q15.csv'));
d20 = zeros(1, 8); d20(Tw.ch + 1) = Tw.w_float_track1_scipy;
d20n = d20 / (2 * sum(d20)); d20r = d20 / max(d20);
T = readtable(fullfile(here, 's7_hybrid_lpxo_ideal.csv'), 'TextType', 'string', 'Delimiter', ',');
Hr = readtable(fullfile(here, 's7_hybrid_lpxo_headroom.csv'), 'TextType', 'string', 'Delimiter', ',');
allok = true;

% ---- (1) banks ------------------------------------------------------------------------------------------------------
designs = {'LPX3-b', 2; 'LPX4-b-cap', 3};
bank = struct();
for i = 1:size(designs, 1)
    nm = designs{i, 1}; nx = designs{i, 2};
    lps = cell(1, nx);
    for k = 1:nx
        lps{k} = getp(nm, sprintf('lowpass_%d', k));
    end
    N = max(cellfun(@numel, lps)); D = (N - 1) / 2;
    for k = 1:nx
        p = (N - numel(lps{k})) / 2; lps{k} = [zeros(1, p), lps{k}, zeros(1, p)];
    end
    dl = zeros(1, N); dl(D + 1) = 1;
    b = cell(1, nx + 1); b{1} = lps{1};
    for k = 2:nx
        b{k} = lps{k} - lps{k - 1};
    end
    b{nx + 1} = dl - lps{nx};
    s = zeros(1, N);
    for k = 1:nx + 1
        s = s + b{k};
    end
    pr = max(abs(s - dl));
    sym = all(cellfun(@(h) max(abs(h - fliplr(h))) < 1e-15, b));
    K = nx + 1; W = zeros(K, 8);
    for k = 1:K
        W(k, :) = getp(nm, sprintf('band_gain_%d', k));
    end
    hax = zeros(1, N);
    for k = 1:K
        hax = hax + 2 * sum(W(k, :)) * b{k};
    end
    ax = max(abs(hax - dl));
    ok = sym && ax < 1e-12; allok = allok && ok;
    out('(1) %s: N = %d, D = %d, [identity] PR err %.1e, symmetric %d, on-axis |sum 2h_c - delta| %.1e -> %s\n', ...
        nm, N, D, pr, sym, ax, pass(ok));
    bank.(strrep(nm, '-', '_')) = struct('b', {b}, 'D', D, 'W', W);
end

% ---- (2) KKT re-derivation for LPX3-b -----------------------------------------------------------------------------------
B = bank.LPX3_b;
bands = [1000 1250 1600 2000 2500 3150 4000];
F7 = [];
for fc = bands
    F7 = [F7, logspace(log10(fc * 2^(-1/6)), log10(fc * 2^(1/6)), 31)]; %#ok<AGROW>
end
p0 = deg2rad(5);
sg = integral(@(a) 10.^(a / 10), -1, 1) / 2 - 2 * (integral(@(a) 10.^(a / 20), -1, 1) / 2) * (integral(@cos, -p0, p0) / (2 * p0)) + 1;
sx2 = (0.5e-3)^2 / 3;
H = zeros(16); g = zeros(16, 1);
for f = F7
    k = 2 * pi * f / c;
    Q = seccov(60, 90, k, xc) + 0.1 * seccov(35, 60, k, xc) + 2 * (sg + k^2 * sx2) * eye(8);
    m = zeroamp(B.b, B.D, f, fs);
    mf = m(2:3)'; H = H + kron(mf * mf', Q) / numel(F7); g = g + kron(mf, Q * (m(1) * d20n')) / numel(F7);
end
C = kron(eye(2), 2 * ones(1, 8));
x = [H, C'; C, zeros(2)] \ [-g; ones(2, 1)];
Wm = [d20n; reshape(x(1:16), 8, 2)'];
dw = max(abs(Wm(:) - B.W(:))) / max(abs(B.W(:)));
ok = dw < 1e-8; allok = allok && ok;
out('(2) LPX3-b band gains re-derived by MATLAB: max relative |diff| = %.2e -> %s\n', dw, pass(ok));

% ---- (3) metrics ---------------------------------------------------------------------------------------------------------
jyt = [30 500; 90 500; 30 1000; 90 1000; 30 2000; 90 2000; 30 4000; 90 4000];
maxd = 0; n = 0;
for i = 1:size(designs, 1)
    nm = designs{i, 1}; Bi = bank.(strrep(nm, '-', '_'));
    A = @(f) zeroamp(Bi.b, Bi.D, f, fs) * Bi.W;
    for fc = [bands 5000]
        fsb = logspace(log10(fc * 2^(-1/6)), log10(fc * 2^(1/6)), 31);
        pp = [0 0];
        for f = fsb
            pp = pp + abs(afp(A(f), f, [0 90], xc, c)).^2;
        end
        maxd = max(maxd, abs(10 * log10(pp(1) / pp(2)) - pick(T, nm, 'R90_band', fc))); n = n + 1;
    end
    for j = 1:size(jyt, 1)
        a = afp(A(jyt(j, 2)), jyt(j, 2), [0 jyt(j, 1)], xc, c);
        maxd = max(maxd, abs(-20 * log10(abs(a(2)) / abs(a(1))) - pick(T, nm, sprintf('JYT_%d_%d_single', jyt(j, 2), jyt(j, 1)), jyt(j, 2)))); n = n + 1;
    end
end
ok = maxd <= 1.5e-3; allok = allok && ok;
out('(3) %d values (8 R90 incl. 5 kHz + 8 JY/T per design, 2 designs): max|MATLAB - numpy CSV| = %.2e dB -> %s\n', n, maxd, pass(ok));

% ---- (4) time-domain peaks for LPX3-b --------------------------------------------------------------------------------
h8 = zeros(8, numel(B.b{1}));
for ch = 1:8
    for k = 1:3
        h8(ch, :) = h8(ch, :) + B.W(k, ch) * B.b{k};
    end
end
fl = linspace(1, 24000, 48000); amax = 0;
for ch = 1:8
    amax = max(amax, max(abs(freqz(h8(ch, :), 1, fl, fs))));
end
maxdt = 0;
for f0 = [100 1000 3000]
    per = round(fs / f0); nn = 0:(2 * fs - 1);
    x = ones(size(nn)); x(mod(nn, per) >= floor(per / 2)) = -1;
    pk = zeros(1, 8);
    for ch = 1:8
        pk(ch) = max(abs(filter(h8(ch, :), 1, x)));
    end
    v = 20 * log10(pk / amax ./ d20r);
    r = Hr(Hr.design == "LPX3-b" & Hr.signal == sprintf('square %d Hz', f0), :);
    maxdt = max(maxdt, max(abs(v - [r.c0 r.c1 r.c2 r.c3 r.c4 r.c5 r.c6 r.c7])));
end
l1 = 20 * log10(sum(abs(h8), 2)' / amax ./ d20r);
r = Hr(Hr.design == "LPX3-b" & Hr.signal == "L1 bound", :);
maxdt = max(maxdt, max(abs(l1 - [r.c0 r.c1 r.c2 r.c3 r.c4 r.c5 r.c6 r.c7])));
ok = maxdt <= 1e-3; allok = allok && ok;
out('(4) LPX3-b squares 100 Hz / 1 kHz / 3 kHz and L1 bound, 8 channels: max|MATLAB - numpy CSV| = %.2e dB -> %s\n', maxdt, pass(ok));
out('OVERALL %s\n', pass(allok));
fclose(fid);
end

function m = zeroamp(b, D, f, fs)
m = zeros(1, numel(b));
for k = 1:numel(b)
    m(k) = real(freqz(b{k}, 1, [f f], fs) * exp(1i * 2 * pi * f * D / fs)) * [1; 0];
end
end

function R = seccov(t1, t2, k, xc)
th = deg2rad(t1:0.25:t2 + 1e-9);
a = 2 * cos(k * sin(th)' * xc);
R = (a' * a) / numel(th);
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
