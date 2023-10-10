from commpy import *
from math import *
from matplotlib import pyplot as plt
import warnings
import numpy as np
import cmath
import random
import scipy.special
from scipy.fft import ifft
from scipy.fft import fft
warnings.simplefilter(action='ignore', category=FutureWarning)
msg = []
for i in range(8):
    msg.append(random.choice([0, 1]))
#print(msg)
#msg = [1,0,0,1,1,0,0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,0,0,1]
modem1 = QAMModem(4)
modem2 = PSKModem(2)
prosto = modem2.modulate(msg)
fig, ax = plt.subplots()
mr = 0
signal = prosto
for i in range(len(signal)):
    element = signal[i]
    g = np.linspace(mr, mr + 8 * pi, 200)
    mr += 8 * pi
    cel = sqrt(2) * sqrt((element.real) ** 2 + (element.imag) ** 2)
    fas = cmath.phase(element)
    u = cel * np.sin(g + fas)
    if i + 1 < len(signal):
        plt.plot([mr, mr], [cel * np.sin(fas), sqrt(2) * sqrt((signal[i + 1].real) ** 2 + (signal[i + 1].imag) ** 2) * np.sin(cmath.phase(signal[i + 1]))], color='k')
    plt.plot(g, u)
plt.grid()
#plt.show()
plt.close()
mr = 0
for i in msg:
    g = np.linspace(mr, mr + 8 * pi, 200)
    plt.plot(g, np.sin(g))

msg1 = []
msg2 = []
msg3 = []
msg4 = []
for i in range(0, len(msg), 4):
    msg1.append(msg[i])
    msg2.append(msg[i+1])
    msg3.append(msg[i+2])
    msg4.append(msg[i+3])
mod1 = modem1.modulate(msg1)
ofmod1 = ifft(mod1)
mod2 = modem2.modulate(msg2)
ofmod2 = ifft(mod2)
mod3 = modem1.modulate(msg3)
ofmod3 = ifft(mod3)
mod4 = modem2.modulate(msg4)
ofmod4 = ifft(mod4)
of_for_peredach = [ofmod1, ofmod2, ofmod3, ofmod4]
ofperedach = []
for i in range(len(ofmod1)):
    ofperedach.append(ofmod1[i])
    ofperedach.append(ofmod2[i])
    ofperedach.append(ofmod3[i])
    ofperedach.append(ofmod4[i])
plt.plot(ofperedach)
#plt.show()
plt.close()
of_for_priem = [(0.07765676184465+0.1521667036239044j), (-0.07107366881247572-0.162610214290351j), (-0.0007005183140029262+0.08805311488020796j), (0.3861145952136338-0.0007356781297843091j), (-0.012812648307770035+0.17287441922240418j), (-0.015955258181846566+0.1316746671611726j), (-0.1721796784445603+0.31269636632980313j), (0.2585278565501775+0.07183800468359677j), (-0.03439278195891687-0.10031826408717598j), (0.1316826789982429-0.2563052510490029j), (-0.2403342471698958-0.057534610792338015j), (-0.16079924617510652+0.14565750022595875j), (-0.15526468103759644-0.1442410278386558j), (-0.058522686534964605-0.35773619911945687j), (-0.15943268787591014+0.06549474496891634j), (-0.2355970213528185+0.20752010631147347j), (0.3053548330559345-0.2967340210961488j), (-0.2024877515685186-0.156422922276944j), (-0.45826123951119213-0.11095539105980817j), (0.22179213482923785+0.28820403580905013j), (-0.12145842704366376-0.1491053726276781j), (0.3939223174632617+0.07737054295340726j), (0.10874594987903691-0.1172687386063853j), (-0.2212053352694057-0.4076962374830963j), (-0.09043154239133108+0.4820254402520256j), (-0.33760011018544717+0.40547467961592804j), (-0.16352248169772624+0.07272141711657329j), (0.1065750008988708+0.14910812841592794j), (-0.013151930888114114+0.19583775215312074j), (0.11391822773147475+0.05923268469809033j), (-0.11606844181074102-0.18932919937029416j), (-0.22482494290102054+0.15020062745221002j), (0.09966041869267092-0.04581480655247479j), (0.04021449465735292-0.10756014183092687j), (-0.1752208705063334+0.21064897664619614j), (-0.24658973904341586+0.12020696899866205j), (0.12389614538362663+0.25774832879751897j), (0.015445798365930814+0.02595822739387105j), (0.45376532282498944+0.24662579170658133j), (-0.06045921885753727+0.08685049351337418j), (-0.34764426861184805+0.1100723208838116j), (-0.12079656720196752-0.2151993352326762j), (-0.049711260860985075-0.11704950436366544j), (-0.006066401759757291+0.08959883598223886j), (0.2553389302309208+0.16955254609191184j), (0.11669980936842869-0.1900110866738797j), (-0.07321603846717673-0.0814234093108163j), (0.12500577455154316+0.21140913980995368j), (-0.10707663141691423+0.20270789379620843j), (0.019451200337556783-0.274791626865998j), (0.033451831416642826-0.3009948334024084j), (0.02464308334876753-0.11459583040449595j)]


for_demod1 = []
for_demod2 = []
for_demod3 = []
for_demod4 = []
for i in range(0, int(len(of_for_priem)), 4):
    for_demod1.append(of_for_priem[i])
    for_demod2.append(of_for_priem[i+1])
    for_demod3.append(of_for_priem[i+2])
    for_demod4.append(of_for_priem[i+3])
demod1 = modem2.demodulate(fft(for_demod1), "hard")
demod2 = modem2.demodulate(fft(for_demod2), "hard")
demod3 = modem2.demodulate(fft(for_demod3), "hard")
demod4 = modem2.demodulate(fft(for_demod4), "hard")
sig_vih = []
for i in range(len(demod1)):
    sig_vih.append(demod1[i])
    sig_vih.append(demod2[i])
    sig_vih.append(demod3[i])
    sig_vih.append(demod4[i])
alt = ""
for i in sig_vih:
    alt += str(i)
#print(alt)
M = 16
P = 16000*(2/log(M, 2))*(erfc(sqrt(10**(23.2/10))*sin(pi/M)))
P2 = 16000*(2*(1-sqrt(M)**(-1))/log(sqrt(M), 2))*(erfc(sqrt(1/2)*sqrt(10**(19.2/10)*3/(M - 1))))
print(P)
print(P2)

modem = PSKModem(4)
mess = [(0.07959669601775266+0.1590036593809164j), (0.08101965493629756-0.1534671682557046j)]

demod = modem.demodulate(mess, "hard")
a = ""
for i in demod:
    a += str(i)
print(a)

"""
mess = [1,0,0,1,1,1,0,1,0,0]
modem = QAMModem(16)
signal = awgn(modem.modulate(mess), 23)
fig1, ax = plt.subplots()
m = "QAM модуляция"
modem.plot_constellation(16)
plt.savefig("vopr3")
ax.spines['left'].set_position(('data', 0.0))
ax.spines['bottom'].set_position(('data', 0.0))
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.axes.get_xaxis().set_ticklabels([])
ax.axes.get_yaxis().set_ticklabels([])
plt.title(str(16) + "-" + m)
for j in signal:
    plt.scatter(j.real, j.imag)
#plt.savefig("sozvezd.png")
plt.close()
vih = []
fig2, ax = plt.subplots()
mr = 0
for i in range(len(signal)):
    element = signal[i]
    g = np.linspace(mr, mr + 8 * math.pi, 200)
    mr += 8 * math.pi
    cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
    fas = cmath.phase(element)
    u = cel * np.sin(g + fas)
    if i + 1 < len(signal):
        plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
            (signal[i + 1].real) ** 2 + (signal[i + 1].imag) ** 2) * np.sin(
            cmath.phase(signal[i + 1]))], color='k')
    plt.plot(g, u)
plt.grid()
ax.set_xlabel('Время, с')
ax.set_ylabel('Амплитуда, В')
#plt.savefig("signal.png")
plt.close()



i=64
modem = PSKModem(i)
modulated = modem.modulate(msg)
t = awgn(modulated, 12)
demodulated = modem.demodulate(t, "hard")
fig1, ax = plt.subplots()
modem.plot_constellation(i)
ax.set_xlabel('I (Синфазная ось)', labelpad=120)
ax.set_ylabel('Q (Квадратурная ось)', labelpad=160)
ax.spines['left'].set_position(('data', 0.0))
ax.spines['bottom'].set_position(('data', 0.0))
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')
ax.axes.get_xaxis().set_ticklabels([])
ax.axes.get_yaxis().set_ticklabels([])
plt.title("64" + "-" + "PSK")
#plt.savefig("64-PSKsozvezd.png")
plt.close()
msg = [0,1,1,0,0,1,1,0,1,0,1,1,1,0,0,1,0,0,0,1,1,0,0,1]
modem1 = PSKModem(64)
modulated1 = modem1.modulate(msg)

modem2 = PSKModem(16)
modulated2 = modem2.modulate(msg)

modem3 = PSKModem(4)
modulated3 = modem3.modulate(msg)

new = []
for i in [modulated1, modulated2, modulated3]:
    for k in i:
        new.append(k)
new_sig = ifft(new)
real = []
mnim = []
mr = 0
for i in new_sig:
    g = np.linspace(mr, mr + 8 * math.pi, 200)
    mr += 8 * math.pi
    cel = math.sqrt(2) * math.sqrt((i.real) ** 2 + (i.imag) ** 2)
    fas = cmath.phase(i)
    u = cel * np.sin(g + fas)
    #real.append(i.real)
    #mnim.append(i.imag)
    plt.plot(g, u)
plt.grid()
plt.show()
plt.close()
plt.plot(new_sig)
plt.show()
plt.close()
print(modem1.demodulate(modulated1, "hard"))
last_sig = awgn(new_sig, 100)
last_sig = fft(last_sig)
mod1 = last_sig[:4]
mod2 = last_sig[4:10]
mod3 = last_sig[10:22]
dem1 = modem1.demodulate(mod1, "hard")
print(dem1)
dem2 = modem2.demodulate(mod2, "hard")
print(dem2)
dem3 = modem3.demodulate(mod3, "hard")
print(dem3)
#plt.plot(new_sig)
#plt.show()
#plt.close()


fig2, ax = plt.subplots()
mr = 0
for i in range(len(modulated)):
    element = modulated[i]
    g = np.linspace(mr, mr + 8 * math.pi, 200)
    mr += 8 * math.pi
    cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
    fas = cmath.phase(element)
    u = cel * np.sin(g + fas)
    if i + 1 < len(modulated):
        plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
            (modulated[i + 1].real) ** 2 + (modulated[i + 1].imag) ** 2) * np.sin(
            cmath.phase(modulated[i + 1]))], color='k')
    plt.plot(g, u)
plt.grid()
ax.set_xlabel('Время, с')
ax.set_ylabel('Амплитуда, В')
#plt.savefig("64-PSKmod.png")
plt.close()

fig3, ax = plt.subplots()
mr = 0
for i in range(len(t)):
    element = t[i]
    g = np.linspace(mr, mr + 8 * math.pi, 200)
    mr += 8 * math.pi
    cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
    fas = cmath.phase(element)
    u = cel * np.sin(g + fas)
    if i + 1 < len(t):
        plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
            (t[i + 1].real) ** 2 + (t[i + 1].imag) ** 2) * np.sin(
            cmath.phase(t[i + 1]))], color='k')
    plt.plot(g, u)
plt.grid()
ax.set_xlabel('Время, с')
ax.set_ylabel('Амплитуда, В')
#plt.savefig("64-PSKawgnlow.png")
plt.close()
print(demodulated)

t = awgn(modulated, 36)
demodulated = modem.demodulate(t, "hard")
fig4, ax = plt.subplots()
mr = 0
for i in range(len(t)):
    element = t[i]
    g = np.linspace(mr, mr + 8 * math.pi, 200)
    mr += 8 * math.pi
    cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
    fas = cmath.phase(element)
    u = cel * np.sin(g + fas)
    if i + 1 < len(t):
        plt.plot([mr, mr], [cel * np.sin(fas), math.sqrt(2) * math.sqrt(
            (t[i + 1].real) ** 2 + (t[i + 1].imag) ** 2) * np.sin(
            cmath.phase(t[i + 1]))], color='k')
    plt.plot(g, u)
plt.grid()
ax.set_xlabel('Время, с')
ax.set_ylabel('Амплитуда, В')
#plt.savefig("64-PSKawgnhigh.png")
plt.close()
print(demodulated)
#0.3% Вероятность ошибки

msg = [1,1,1,1,1,1,1,1,1,1]
f = [2,0.5,0.5,2,2,0.5,0.5,2,0.5,2]
vih = []
for i in msg:
    vih.append((2 * i + 1) + (2 * i + 1) * (1j))
print(vih)
mr = 0
for i in range(len(vih)):
    element = vih[i]
    g = np.linspace(mr, mr + 8 * math.pi, 200)
    mr += 8 * math.pi
    cel = math.sqrt(2) * math.sqrt((element.real) ** 2 + (element.imag) ** 2)
    fas = cmath.phase(element)
    u = cel * np.sin(g*f[i])
    plt.plot(g, u)
plt.grid()
plt.show()
plt.close()
"""