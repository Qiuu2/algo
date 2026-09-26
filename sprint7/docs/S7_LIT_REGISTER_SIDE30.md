# 外部文献入库登记：侧面抑制 30 dB 检索（铁律六 / C8）

> **登记日期**：2026-09-26，与下载同日，不超过 24h。
> **来源**：3 路文献检索子代理，均在 2026-09-26 由 PM 派出：A 声区/声对比度、B 音柱工程实践、C 稳健设计与校准。只取开放获取版本，未使用任何影子图书馆。
> **存放**：`/home/it1234/algorithm_speaker/knowledge_base/papers/2026-09_side30/`（仓库外，是 CTO 的本地论文库，不进 git）。本登记表进 git，用 md5 锁定文件身份。
> **性质**：文中数字是各论文作者在自己硬件上的结果，对本项目属**外部证据**，不是本项目的 L1/L2。引用时写成"文献 X 报告…"，不得写成我方实测。
> **索引与付费墙清单**：同目录 `README_论文索引.md`，其中 12 篇付费墙论文附 DOI。

| # | 文件（相对 2026-09_side30/） | 文献 | DOI / 出处 | md5 | 字节 |
|---|---|---|---|---|---|
| 1 | A_sound_zones/Betlehem_2015_Personal_sound_zones_SPM_overview.pdf | Betlehem, Zhang, Poletti, Abhayapala 2015, IEEE SPM 32(2):81 | 10.1109/MSP.2014.2360707 | c4a38c027f3659b0e1fd9d8bab2467df | 1907461 |
| 2 | A_sound_zones/Huang_Lu_2024_Speaker_selection_condition_number_sound_zone_CN.pdf | 黄洋…卢晶 2024, 声学学报 49(6) | 10.12395/0371-0025.2024261 | 0dc0f9894d2342cad79acfac2669cca7 | 1391635 |
| 3 | A_sound_zones/Zhu_2017_Robust_ACC_reduced_insitu_measurement.pdf | Zhu, Coleman, Wu, Yang 2017, JAES 65(6):460 | 10.17743/jaes.2017.0016 | d51972344539e0aebd6332cb859b5393 | 868131 |
| 4 | A_sound_zones/Zhu_2019_Robust_personal_audio_geometry_SVD_modal_domain.pdf | Zhu et al. 2019, IEEE/ACM TASLP 27(3):610（录用稿） | 10.1109/TASLP.2018.2889927 | beb8228251f61774c209d762dc122c7d | 1382087 |
| 5 | B_column_practice/deVries_1997_ConceptsDirectivityControlledArrays.pdf | de Vries & van Beuningen 1997, ASA meeting (Duran Audio) | — | cc62357db8f7cbcd72e350398be8c658 | 206253 |
| 6 | B_column_practice/MeyerSound_2002_DSPBeamSteeringModernLineArrays.pdf | Meyer Sound 2002 tech report | — | 802579793ab1714e8ff58a4ae330622a | 814752 |
| 7 | B_column_practice/Start_2001_DDSArraysNearFieldHolography.pdf | Start & van Beuningen 2001, Proc. IOA | — | 5dbb6fa23b2295b9eea06c505f802e69 | 575201 |
| 8 | B_column_practice/Start_2003_DDSControlledCardioidArrays.pdf | Start & van Beuningen 2003, Proc. IOA 25(8) | — | b271c596ce7d4dcd4f8cb419032391bb | 345625 |
| 9 | B_column_practice/Straube_2015_EvaluationStrategiesOptimizationLSA.pdf | Straube et al. 2015, AES 59th Int. Conf. | — | bd8ec41a2fc6803a3b881499eeabf739 | 7398116 |
| 10 | B_column_practice/Straube_2018_MixedAnalyticalNumericalFilterDesignLSA.pdf | Straube, Schultz, Makarski, Weinzierl 2018, JAES 66(9):690（postprint） | 10.17743/jaes.2018.0043 | 058dd1b658ed3429da5312d1f90a3878 | 944012 |
| 11 | B_column_practice/Thompson_2008_RealWorldLineArrayOptimisation.pdf | Thompson 2008, Proc. IOA 30(6) | — | c961014bdaaff9b51434c9fc623582fa | 1826802 |
| 12 | B_column_practice/vanBeuningen_2000_OptimizingDirectivityDSPControlledArrays.pdf | van Beuningen & Start 2000, Proc. IOA 22(6):17 | 10.25144/18638 | f19b959ac87af3bb255cbb5b84b8e086 | 1528252 |
| 13 | C_robust_calibration/Chojnacki_2024_Sensors_DispersionTransducerParams_fulltext_EuropePMC.xml | Chojnacki 2024, Sensors 24(15):4958（CC-BY，全文 XML） | 10.3390/s24154958 | e5ae47f841bbf1000beb6c0c6bbfcc65 | 103168 |
| 14 | C_robust_calibration/Doclo_2003_ICASSP_RobustBroadbandSpeechBeamformersMicErrors.pdf | Doclo & Moonen 2003, ICASSP V-473（会议版） | 期刊版 10.1109/TSP.2003.816885 | 5c045cff94780143b04c229bafdd68d9 | 223608 |
| 15 | C_robust_calibration/Gilbert_1955_BSTJ_OptimumArraysRandomVariations.pdf | Gilbert & Morgan 1955, BSTJ 34(3):637（archive.org 扫描件） | — | 6d122570379c699ebfb36d10f9833a44 | 12568493 |
| 16 | C_robust_calibration/Tashev_2005_BeamformerSensitivityMicManufacturingTolerances.pdf | Tashev 2005, Microsoft Research | — | 01f26d1eccb7e40222fea5f9d4c4d007 | 56449 |

**已在本地库、本次被引用的两份**（2026-05-26 入库）：
- Van Trees 2002《Optimum Array Processing》§2.6.3，式 (2.205)–(2.211)：误差底噪 = ‖w‖² × 误差方差。
- Boone, Cho, Ih 2009, JAES 57(5)：设计时计入每只喇叭的实测指向性，指向性 +2–3 dB。

**措辞约束**（critic R2 MINOR-5）：
- Start 2003 的"up to 20 dB"是低于 630 Hz 的**附加后向（心形）**抑制，论文自述低频后向值未能实测验证，**不得**当作侧向抑制的实测数据点。
- Zhu 2017 的 11–17.5 dB 是**房间声区对比度**，和远场前/侧比不是同一指标。
- 对外只能说"在检索到的公开文献中未找到可比的 ≥30 dB 实测证据"，不得暗示存在物理上限。
