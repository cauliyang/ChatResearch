## Paper:5

1.  Title: Connectivity-based Meta-Bands: A new approach for automatic frequency band identification in connectivity analyses （连接性元子带:一种自动化的频带识别方法，用于连接性分析）

                 2. Authors: Víctor Rodríguez-González, Pablo Núñez, Carlos Gómez, Yoshihito Shigihara, Hideyuki Hoshi, Miguel Ángel Tola-Arribas, Mónica Cano, Ángel Guerrero, David García-Azorín, Roberto Hornero, Jesús Poza


                 3. Affiliation: Biomedical Engineering Group, University of Valladolid （瓦拉多利德大学生物医学工程组）


                 4. Keywords: Connectivity-based Meta-Bands, functional connectivity, frequency bands, EEG, MEG


                 5. Urls: https://doi.org/10.1101/2023.03.30.534879, Github: None


                 6. Summary:

                    - (1):The research background of this article is that the majority of electroencephalographic (EEG) and magnetoencephalographic (MEG) studies filter and analyze neural signals in specific frequency ranges, known as "canonical" frequency bands, but this segmentation is not exempt from limitations, mainly due to the lack of adaptation to the neural idiosyncrasies of each individual.

                    - (2):Past methods include fixed canonical frequency bands and subject-adaptive frequency bands that rely on local activation patterns. The proposed approach is well motivated as it accounts for the frequency-dependent network structure and provides more personalized analyses.

                    - (3):The research methodology proposed in this paper is an unsupervised band segmentation method based on the topological similarity of functional neural networks across frequencies. The Connectivity-based Meta-Bands (CMB) algorithm identifies communities in the frequency domain showing a similar network topology.

                    - (4):The CMB algorithm provides personalized analyses that adapt to the individual idiosyncrasies of neural activity of each subject, allowing for connectivity analyses accounting for the underlying frequency structure. The sensitivity and robustness of this approach were tested on resting-state neural activity of 195 cognitively healthy subjects from three different databases (MEG: 123 subjects; EEG1: 27 subjects; EEG2: 45 subjects). The results show that the classical approaches to band segmentation reflect the underlying network topologies at the group level for MEG signals, but fail to adapt to individual differentiating patterns revealed by the CMB methodology, which fully accounts for subject-specific patterns. To the best of their knowledge, this is the first study that proposes an unsupervised band segmentation method based on the topological similarity of functional neural networks across frequencies.

2.  Conclusion:

- (1): The significance of this piece of work lies in providing a new approach for automatic frequency band identification in connectivity analyses, which fully accounts for subject-specific patterns and allows for personalized analyses that adapt to the individual idiosyncrasies of neural activity.

- (2): Innovation point: The Connectivity-based Meta-Bands (CMB) algorithm proposed in this article is an unsupervised band segmentation method based on the topological similarity of functional neural networks across frequencies, which is a novel approach for identifying frequency bands.

Performance: The results of the experiments on resting-state neural activity of 195 cognitively healthy subjects from three different databases show that the CMB algorithm outperforms classical approaches to band segmentation in terms of accounting for the underlying frequency structure and identifying subject-specific patterns.

Workload: While the CMB algorithm requires significant computational resources, it is feasible for practical application and provides valuable personalized analyses. Overall, this article makes a valuable contribution to the field of bioinformatics and provides a promising direction for future studies.
