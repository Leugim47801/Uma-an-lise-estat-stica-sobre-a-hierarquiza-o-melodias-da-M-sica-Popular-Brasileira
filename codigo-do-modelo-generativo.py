!pip install mido

import numpy as np
import random
from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo


class estrutura():
    def __init__(self, UT = {'D': 0.7, 'T': 0.3}, LT = {'D': 0.6, 'T': 0.4}, UPh_D = {1: 0.8, 2: 0.2},
                 UPh_T = {1: 0.7, 2: 0.2, 3: 0.1}, Tn_diff = {-1: 0.1, 0: 0.8, 1: 0.1},
                 prob_para_notas = {0: 0.01, 1: 0.38, 2: 0.74, 3: 0.94},
                 bpm=120, An=0.05, nome="Arquivo Midi.mid"):
        self.UT = UT
        self.LT = LT
        self.UPh_D = UPh_D
        self.UPh_T = UPh_T
        self.BPM = bpm
        self.BPM_em_pips = (60 * 1000 / self.BPM) / 50
        self.T1 = self.BPM_em_pips
        self.An = An
        self.Tn_diff = Tn_diff
        self.surf = {}
        self.prob_para_notas = prob_para_notas
        self.nome_arquivo = nome

        self.nivel2_gerado = False
        self.nivel3_gerado = False
        self.nivel1_gerado = False
        self.pontos_de_ataque_gerados = False

    def gerar_nivel2(self):  # ===================================================
        self.surf[0] = {'Nivel': 2, 'Nota': None}

        self.surf[round(self.T1)] = {'Nivel': 2, 'Nota': None}

        tnm1 = self.T1

        while np.random.random() > self.An:
            tn_diff = random.choices(
                population=list(self.Tn_diff.keys()),
                weights=list(self.Tn_diff.values()),
                k=1
            )[0]
            self.surf[round(tnm1 + self.BPM_em_pips + tn_diff)] = {'Nivel': 2, 'Nota': None}
            tnm1 = tnm1 + self.BPM_em_pips + tn_diff

        self.nivel2_gerado = True

        return self.surf

    def gerar_nivel3(self):  # ===================================================

        if self.nivel2_gerado == False:
          print("Aviso: Nível 2 não foi gerado. Gerando Nível 2")
          self.gerar_nivel2()
          self.nivel2_gerado = True
        else:
            pass

        self.Qual_UT = random.choices(
            population=list(self.UT.keys()),
            weights=list(self.UT.values()),
            k=1
        )[0]

        if self.Qual_UT == 'D':
            self.Qual_UPh = random.choices(
                population=list(self.UPh_D.keys()),
                weights=list(self.UPh_D.values()),
                k=1
            )[0]

        elif self.Qual_UT == 'T':
            self.Qual_UPh = random.choices(
                population=list(self.UPh_T.keys()),
                weights=list(self.UPh_T.values()),
                k=1
            )[0]

        self.Niveis2_seguidos = []

        for n_pip in list(self.surf)[self.Qual_UPh - 1:]:
            if self.surf[n_pip]['Nivel'] == 2:
                self.Niveis2_seguidos.append(n_pip)
                Mudar_de_nivel = None

                if self.Qual_UT == 'D' and len(self.Niveis2_seguidos) == 2:
                    Mudar_de_nivel = self.Niveis2_seguidos[0]

                elif self.Qual_UT == 'T' and len(self.Niveis2_seguidos) == 3:
                    Mudar_de_nivel = self.Niveis2_seguidos[0]

                if Mudar_de_nivel != None:
                    self.surf[Mudar_de_nivel]['Nivel'] = 3
                    self.Niveis2_seguidos = []
            else:
                self.Niveis2_seguidos = []

        if self.Qual_UT == 'D' and len(list(self.surf)[self.Qual_UPh - 1:]) % 2 != 0:
            self.surf[list(self.surf)[self.Qual_UPh - 1:][-(len(list(self.surf)[self.Qual_UPh - 1:]) % 2)]]['Nivel'] = 3
        elif self.Qual_UT == 'T' and len(list(self.surf)[self.Qual_UPh - 1:]) % 3 != 0:
            self.surf[list(self.surf)[self.Qual_UPh - 1:][-(len(list(self.surf)[self.Qual_UPh - 1:]) % 3)]]['Nivel'] = 3

        self.nivel3_gerado = True

        return self.surf

    def gerar_nivel1(self):  # ===================================================

        if self.nivel3_gerado == False:
          print("Aviso: Nível 3 não foi gerado. Gerando Nível 3")
          self.gerar_nivel3() # Corrected: Should call gerar_nivel3 to initialize Qual_UT
          self.nivel3_gerado = True
        else:
            pass

        self.Qual_LT = random.choices(
            population=list(self.LT.keys()),
            weights=list(self.LT.values()),
            k=1
        )[0]

        self.os_pips = list(self.surf.keys())

        for i in range(len(self.os_pips) - 1):
            pip_atual = self.os_pips[i]
            pip_proximo = self.os_pips[i + 1]
            intervalo = pip_proximo - pip_atual

            if self.Qual_LT == 'D':
                DBn = 0.5 * intervalo
                novo_pip = pip_atual + DBn
                self.surf[round(novo_pip)] = {'Nivel': 1, 'Nota': None}

            elif self.Qual_LT == 'T':
                TBn1 = intervalo / 3
                TBn2 = 2 * intervalo / 3
                novo_pip_1 = pip_atual + TBn1
                novo_pip_2 = pip_atual + TBn2
                self.surf[round(novo_pip_1)] = {'Nivel': 1, 'Nota': None}
                self.surf[round(novo_pip_2)] = {'Nivel': 1, 'Nota': None}

        self.surf = dict(sorted(self.surf.items()))

        self.nivel1_gerado = True

        return self.surf

    def gerar_pontos_de_ataque(self):  # =========================================

        if self.nivel1_gerado == False:
          print("Aviso: Nível 1 não foi gerado. Gerando Nível 1")
          self.gerar_nivel1()
          self.nivel1_gerado = True
        else:
            pass

        self.surf[0]['Nota'] = True

        for pip in range(1, list(self.surf)[-1] + 1):
            if pip not in list(self.surf):
                if random.random() < self.prob_para_notas[0]:
                    self.surf[pip] = {'Nivel': 0, 'Nota': True}
            else:
                if self.surf[pip]['Nivel'] == 1:
                    if random.random() < self.prob_para_notas[1]:
                        self.surf[pip]['Nota'] = True
                elif self.surf[pip]['Nivel'] == 2:
                    if random.random() < self.prob_para_notas[2]:
                        self.surf[pip]['Nota'] = True
                elif self.surf[pip]['Nivel'] == 3:
                    if random.random() < self.prob_para_notas[3]:
                        self.surf[pip]['Nota'] = True

        self.surf = dict(sorted(self.surf.items()))

        print(f"UT: {self.Qual_UT}")
        print(f"LT: {self.Qual_LT}")
        print(f"UPh: {self.Qual_UPh}")

        self.pontos_de_ataque_gerados = True

        return self.surf

    def ms_para_ticks(self, ms, ticks_per_beat, tempo):  # =======================
        return round(ms * ticks_per_beat / (tempo / 1000))

    def gerar_midi(self, pitch=60, duracao_final_ms=1000):
        self.surf = self.gerar_pontos_de_ataque()
        ms_por_pip = 50

        mido_file = MidiFile()
        track = MidiTrack()
        mido_file.tracks.append(track)

        tempo = bpm2tempo(self.BPM)
        track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

        ticks_per_beat = mido_file.ticks_per_beat

        instantes_notas = sorted(
            t for t, info in self.surf.items()
            if info['Nota'] is True
        )

        ultimo_tempo_ms = 0

        for i, inicio in enumerate(instantes_notas):

            inicio_ms = inicio * ms_por_pip

            delta_ms = inicio_ms - ultimo_tempo_ms
            delta_ticks = self.ms_para_ticks(
                delta_ms,
                ticks_per_beat,
                tempo
            )

            if i < len(instantes_notas) - 1:
                fim = instantes_notas[i + 1]
                duracao_ms = (fim - inicio) * ms_por_pip
            else:
                duracao_ms = duracao_final_ms

            duracao_ticks = self.ms_para_ticks(
                duracao_ms,
                ticks_per_beat,
                tempo
            )

            track.append(Message(
                'note_on',
                note=pitch,
                velocity=64,
                time=delta_ticks
            ))

            track.append(Message(
                'note_off',
                note=pitch,
                velocity=64,
                time=duracao_ticks
            ))

            ultimo_tempo_ms = inicio_ms + duracao_ms

        mido_file.save(self.nome_arquivo)
        print(f"Arquivo MIDI salvo com sucesso como: {self.nome_arquivo}")
