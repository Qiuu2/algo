% S7 / B5 dual-track (iron rule 7) -- INDEPENDENT MATLAB re-computation of the baseline rows.
% [L2/MATLAB]. Does NOT read any numpy output; implements its own array factor, -6 dB full-angle
% beam width, peak side-lobe search and closed-form DI.
% Model: N=16 isotropic point sources, d=55 mm, centred, c=343 m/s (explicit, skill N.2.1),
% far-field AF(theta)=sum w_n exp(j k x_n sin theta), theta=0 broadside, 0.01 deg grid.
% Rows: Dolph-20 (chebwin(16,20)/max) @1k/2k/4k BW6+SLL+DI ; uniform @1k ; Dolph-30 @1k ;
%       Kaiser beta=5 @1k ; Taylor(16,nbar=4,sll=25) @1k.
% Output: prints "CSVROW,<row>,<f>,<BW6>,<SLL>,<DI>" lines and writes s7_matlab_crosscheck.csv next to this file.
% NOTE: local functions in a MATLAB script must be placed at the END of the file.
outdir = fileparts(mfilename('fullpath'));
if isempty(outdir), outdir = pwd; end
N = 16;
rows = {};
w20 = chebwin(N,20);  w30 = chebwin(N,30);  wk5 = kaiser(N,5);  wt25 = taylorwin(N,4,-25);  wu = ones(N,1);
[bw,sll,di] = evalw(w20,1000);  rows(end+1,:) = {'dolph20',1000,bw,sll,di};
[bw,sll,di] = evalw(w20,2000);  rows(end+1,:) = {'dolph20',2000,bw,sll,di};
[bw,sll,di] = evalw(w20,4000);  rows(end+1,:) = {'dolph20',4000,bw,sll,di};
[bw,sll,di] = evalw(wu,1000);   rows(end+1,:) = {'uniform',1000,bw,sll,di};
[bw,sll,di] = evalw(w30,1000);  rows(end+1,:) = {'dolph30',1000,bw,sll,di};
[bw,sll,di] = evalw(wk5,1000);  rows(end+1,:) = {'kaiser_b5',1000,bw,sll,di};
[bw,sll,di] = evalw(wt25,1000); rows(end+1,:) = {'taylor25_nbar4',1000,bw,sll,di};
fid = fopen(fullfile(outdir,'s7_matlab_crosscheck.csv'),'w');
fprintf(fid,'window,freq_hz,BW6dB_full_deg,peak_SLL_dB,DI_dB,track\n');
for i = 1:size(rows,1)
    fprintf(fid,'%s,%d,%.4f,%.4f,%.4f,L2/MATLAB\n',rows{i,1},rows{i,2},rows{i,3},rows{i,4},rows{i,5});
    fprintf('CSVROW,%s,%d,%.4f,%.4f,%.4f\n',rows{i,1},rows{i,2},rows{i,3},rows{i,4},rows{i,5});
end
fclose(fid);
fprintf('MATLAB %s ; f_grating=c/d=%.0f Hz ; PropagationSpeed c=343 m/s explicit\n', version, 343/0.055);

function [bw, sll, di] = evalw(w, f)
    % local function: does NOT see the script workspace -> constants restated here
    c = 343;  N = 16;  d = 0.055;                 % PropagationSpeed explicit (skill N.2.1)
    x = ((0:N-1) - (N-1)/2) * d;
    ang = -90:0.01:90;
    w = w(:).' / max(w);
    k = 2*pi*f/c;
    AF = abs(exp(1j*k*sind(ang).'*x) * w.');
    P = 20*log10(AF/max(AF));
    [~, i0] = max(P);
    thr = P(i0) - 6;
    iR = i0; while iR < numel(P) && P(iR) > thr, iR = iR + 1; end
    iL = i0; while iL > 1 && P(iL) > thr, iL = iL - 1; end
    aR = interp1([P(iR) P(iR-1)], [ang(iR) ang(iR-1)], thr);
    aL = interp1([P(iL) P(iL+1)], [ang(iL) ang(iL+1)], thr);
    bw = aR - aL;
    % side lobe: main lobe = out to first local minimum each side
    jR = i0; while jR < numel(P) && P(jR+1) <= P(jR), jR = jR + 1; end
    jL = i0; while jL > 1 && P(jL-1) <= P(jL), jL = jL - 1; end
    mask = true(size(P)); mask(jL:jR) = false;
    sll = max(P(mask)) - P(i0);
    % DI closed form (3-D isotropic): |sum w|^2 / sum_ij w_i w_j sinc(k|xi-xj|)
    dx = k*abs(x.' - x);
    G = sin(dx)./dx; G(dx==0) = 1;
    di = 10*log10(sum(w)^2 / (w*G*w.'));
end
