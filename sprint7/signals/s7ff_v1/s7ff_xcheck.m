% s7ff_xcheck.m -- MATLAB second track for the s7ff_v1 signal package (iron rule 7).
%
% Independent of the Python generator and checker: reads every delivered WAV with audioinfo/audioread,
% recomputes header facts, 35 s steady RMS, peak, in-band energy fraction, energy beyond one octave from
% the band edges (E1), energy in the adjacent 1/3-oct regions (E2), PSD at the adjacent 1/3-oct centres
% (P2, +/-1/48 oct around fc*2^(+/-1/3) and the neighbouring nominal centres), level-step residual and the silence
% file with plain fft (no toolbox functions), applies the same gates as README.md, then compares the
% numbers with S7FF_V1_METRICS.csv written by s7ff_check.py.
% Output: s7ff_xcheck.log in this folder.  Run: run_matlab_file / >> s7ff_xcheck
here   = fileparts(mfilename('fullpath'));
wavdir = fullfile(here, 'wav');
lg     = fopen(fullfile(here, 's7ff_xcheck.log'), 'w');
assert(lg > 0, 'cannot open s7ff_xcheck.log');

FS = 48000; NTOT = 1728000; M = 24000; N = NTOT - 2*M; FULL = 2^23;
bands  = [500 630 800 1000 1250 1600 2000 2500 3150 4000 5000 6300];
nominal = [315 400 500 630 800 1000 1250 1600 2000 2500 3150 4000 5000 6300 8000 10000];
levels = [0 10 20 30 40];
T = readtable(fullfile(here, 'S7FF_V1_METRICS.csv'), 'TextType', 'string', 'Delimiter', ',');

say(lg, 's7ff_xcheck (MATLAB %s) %s\n', version, char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss')));
say(lg, '%-26s %9s %9s %10s %8s %8s %8s %8s | %9s %9s %8s %8s %8s %9s\n', 'file', 'rms_dB', 'peak_dB', 'inband', ...
    'E1', 'E2', 'P2', 'L_lsb', 'd_rms', 'd_peak', 'd_E1', 'd_E2', 'd_P2', 'd_L');
nfail = 0; worst = zeros(1, 6);   % max |MATLAB - Python| for rms, peak, E1, E2, P2, L
f = (0:N/2)' * FS / N;
for fc = bands
    lo = fc * 2^(-1/6); hi = fc * 2^(1/6);
    inb = f >= lo & f <= hi;  far = f < lo/2 | f > 2*hi;
    adjlo = f >= fc * 2^(-1/2) & f < lo;  adjhi = f > hi & f <= fc * 2^(1/2);
    y0 = [];
    for k = levels
        if k == 0, tag = '0dB'; else, tag = sprintf('m%ddB', k); end
        nm = sprintf('s7ff_v1_%04dHz_%s.wav', fc, tag);
        fp = fullfile(wavdir, nm);
        fails = {};
        info = audioinfo(fp);
        if info.SampleRate ~= FS || info.BitsPerSample ~= 24 || info.NumChannels ~= 1 || info.TotalSamples ~= NTOT
            fails{end+1} = sprintf('H: %d Hz %d bit %d ch %d samples', info.SampleRate, info.BitsPerSample, info.NumChannels, info.TotalSamples); %#ok<SAGROW>
        end
        y = audioread(fp);                         % double, int24 / 2^23
        if max(abs(y*FULL - round(y*FULL))) > 1e-6
            fails{end+1} = 'scale: samples are not integer multiples of 2^-23'; %#ok<SAGROW>
        end
        s = y(M+1:M+N);
        rmsdb  = 20*log10(sqrt(mean(s.^2)));
        peakdb = 20*log10(max(abs(y)));
        S = fft(s); P = abs(S(1:N/2+1)).^2; P(2:end-1) = 2*P(2:end-1);
        Ein  = sum(P(inb));
        frac = Ein / sum(P);
        E1   = 10*log10(sum(P(far)) / Ein);
        E2   = 10*log10(max(sum(P(adjlo)), sum(P(adjhi))) / Ein);
        ni = find(nominal == fc);
        P2 = -Inf;
        for c = [fc*2^(-1/3), fc*2^(1/3), nominal(ni-1), nominal(ni+1)]
            w = f >= c*2^(-1/48) & f < c*2^(1/48);
            P2 = max(P2, 10*log10(mean(P(w)) / mean(P(inb))));
        end
        if abs(rmsdb - (-23 - k)) > 0.01, fails{end+1} = sprintf('R: %.4f dB', rmsdb); end %#ok<SAGROW>
        if P2 > -30, fails{end+1} = sprintf('P2: %.1f dB', P2); end %#ok<SAGROW>
        if peakdb > -3.0, fails{end+1} = sprintf('P: %.3f dB', peakdb); end %#ok<SAGROW>
        if frac < 0.999, fails{end+1} = sprintf('B: %.6f', frac); end %#ok<SAGROW>
        if E1 > -50, fails{end+1} = sprintf('E1: %.1f dB', E1); end %#ok<SAGROW>
        if E2 > -30, fails{end+1} = sprintf('E2: %.1f dB', E2); end %#ok<SAGROW>
        if abs(y(1)) > 1/FULL || abs(y(end)) > 1/FULL, fails{end+1} = 'F: click at start/stop'; end %#ok<SAGROW>
        Llsb = NaN;
        if k == 0
            y0 = y;
        else
            Llsb = sqrt(mean(((y - y0 * 10^(-k/20)) * FULL).^2));
            if Llsb > 1, fails{end+1} = sprintf('L: %.2f LSB', Llsb); end %#ok<SAGROW>
        end
        row = T(T.file == nm, :);
        d = [abs(rmsdb - row.R_rms_dB), abs(peakdb - row.P_peak_dB), abs(E1 - row.E1_far_energy_dB), ...
             abs(E2 - row.E2_adj_energy_dB), abs(P2 - row.P2_adj_psd_dB), 0];
        if k > 0, d(6) = abs(Llsb - row.L_resid_lsb); end
        worst = max(worst, d);
        say(lg, '%-26s %9.4f %9.4f %10.7f %8.2f %8.2f %8.2f %8.3f | %9.1e %9.1e %8.1e %8.1e %8.1e %9.1e %s\n', ...
            erase(nm, 's7ff_v1_'), rmsdb, peakdb, frac, E1, E2, P2, Llsb, d, strjoin(string(fails), '; '));
        nfail = nfail + numel(fails);
    end
end
sil = audioread(fullfile(wavdir, 's7ff_v1_silence.wav'));
info = audioinfo(fullfile(wavdir, 's7ff_v1_silence.wav'));
if any(sil ~= 0) || info.TotalSamples ~= NTOT || info.BitsPerSample ~= 24
    nfail = nfail + 1; say(lg, 'silence file: FAIL\n');
else
    say(lg, 'silence file: %d samples, all zero, 24 bit -> PASS\n', info.TotalSamples);
end
tol = [0.001 0.001 0.1 0.1 0.1 0.01];
agree = all(worst <= tol);
say(lg, '\nmax |MATLAB - Python|: rms %.2e dB, peak %.2e dB, E1 %.2e dB, E2 %.2e dB, P2 %.2e dB, L %.2e LSB (tolerance %s)\n', worst, mat2str(tol));
say(lg, 'MATLAB gate failures: %d | agreement with s7ff_check.py: %s | OVERALL %s\n', nfail, ...
    string(agree), string(nfail == 0 && agree));
fclose(lg);

function say(lg, varargin)
% print to the command window and to the log
fprintf(varargin{:});
fprintf(lg, varargin{:});
end
