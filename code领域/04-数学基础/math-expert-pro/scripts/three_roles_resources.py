#!/usr/bin/env python3
"""
475 本书 × 三角色 × 网络资源 深度档案生成器
=============================================
为每本书生成一份 .md，包含：
  - 三角色定位（教材/工程师/研究员）
  - 每角色各自的网络资源（视频/论文/代码/形式化/社区）
  - 综合学习路径
"""
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

INDEX_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/书籍索引")
OUTPUT_ROOT = Path("/mnt/c/workspace/math-expert-pro/09-crosstext/三角色资源档案")

# === 主题 → 网络资源映射 ===
THEME_RESOURCES = {
    "分析·微积分": {
        "video": [
            ("3Blue1Brown《微积分的本质》", "https://www.3blue1brown.com/topics/calculus"),
            ("MIT OCW 18.01 单变量微积分", "https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/"),
            ("Khan Academy Calculus", "https://www.khanacademy.org/math/calculus-1"),
            ("Professor Leonard Calculus", "https://www.youtube.com/@ProfessorLeonard"),
        ],
        "paper": [
            ("Cauchy 1821 原始论文（Cours d'Analyse）", "https://gallica.bnf.fr/"),
            ("Wigner 1960《数学的不合理有效性》", "https://www.maths.ed.ac.uk/~v1ranick/papers/wigner.pdf"),
        ],
        "code": [
            ("SymPy Calculus", "https://docs.sympy.org/latest/modules/calculus/index.html"),
            ("Desmos 在线计算器", "https://www.desmos.com/calculator"),
            ("GeoGebra Calculus", "https://www.geogebra.org/calculus"),
        ],
        "lean": [
            ("Mathlib.Topology.Continuity", "https://leanprover-community.github.io/mathlib4_docs/"),
            ("Mathlib.Deriv", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Math StackExchange [calculus]", "https://math.stackexchange.com/questions/tagged/calculus"),
            ("r/calculus", "https://www.reddit.com/r/calculus/"),
        ],
    },
    "代数·线性": {
        "video": [
            ("3Blue1Brown《线性代数的本质》", "https://www.3blue1brown.com/topics/linear-algebra"),
            ("MIT OCW 18.06 Gilbert Strang", "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/"),
            ("Khan Academy Linear Algebra", "https://www.khanacademy.org/math/linear-algebra"),
        ],
        "paper": [
            ("Axler 1995《Down with Determinants!》", "https://www.axler.net/DwD.pdf"),
        ],
        "code": [
            ("numpy.linalg 文档", "https://numpy.org/doc/stable/reference/routines.linalg.html"),
            ("Eigen C++ 库", "https://eigen.tuxfamily.org/"),
            ("JAX 线性代数", "https://jax.readthedocs.io/"),
        ],
        "lean": [
            ("Mathlib.LinearAlgebra.Matrix", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Matrix/"),
            ("Mathlib.LinearAlgebra.Eigenspace", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Math StackExchange [linear-algebra]", "https://math.stackexchange.com/questions/tagged/linear-algebra"),
            ("Eigen 论坛", "https://forum.eigen.tuxfamily.org/"),
        ],
    },
    "概率·统计": {
        "video": [
            ("Harvard Stat 110 Joe Blitzstein", "https://projects.iq.harvard.edu/stat110"),
            ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability"),
            ("3Blue1Brown 概率（二项分布）", "https://www.youtube.com/watch?v=8idrVW1116I"),
        ],
        "paper": [
            ("Shannon 1948《通信的数学理论》", "https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf"),
            ("Bayes 1763 原始论文", "https://statweb.stanford.edu/~owen/tables/Bayes-1763.pdf"),
        ],
        "code": [
            ("scipy.stats", "https://docs.scipy.org/doc/scipy/reference/stats.html"),
            ("PyMC3 贝叶斯", "https://docs.pymc.io/"),
            ("Stan 贝叶斯", "https://mc-stan.org/"),
        ],
        "lean": [
            ("Mathlib.Probability.ProbabilitySpace", "https://leanprover-community.github.io/mathlib4_docs/"),
            ("Mathlib.Probability.Distributions", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Cross Validated [statistics]", "https://stats.stackexchange.com/"),
            ("r/statistics", "https://www.reddit.com/r/statistics/"),
            ("PyMC Discourse", "https://discourse.pymc.io/"),
        ],
    },
    "动力系统/ODE/PDE": {
        "video": [
            ("Steven Strogatz《非线性动力学与混沌》Cornell", "https://www.youtube.com/playlist?list=PLbN57C5Zdl6j_qJA-pARJnKsmROzPnO9V"),
            ("MIT OCW 18.03 微分方程", "https://ocw.mit.edu/courses/18-03-differential-equations-spring-2010/"),
            ("3Blue1Brown 微分方程", "https://www.youtube.com/watch?v=p_di4Zn4wz4"),
        ],
        "paper": [
            ("Imperial Ferguson 2020 COVID 报告", "https://www.imperial.ac.uk/mrc-global-infectious-disease-analysis/covid-19/"),
            ("Lorenz 1963 混沌原始论文", "https://journals.ametsoc.org/view/journals/atsc/20/2/1520-0469_1963_020_0130_dnf_2_0_co_2.xml"),
        ],
        "code": [
            ("scipy.integrate.odeint", "https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html"),
            ("Julia DifferentialEquations.jl", "https://diffeq.sciml.ai/"),
            ("PyDy 多体动力学", "http://www.pydy.org/"),
        ],
        "lean": [
            ("Mathlib.ODE", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/ODE/"),
        ],
        "community": [
            ("Math StackExchange [differential-equations]", "https://math.stackexchange.com/questions/tagged/differential-equations"),
            ("Julia Discourse [diffeq]", "https://discourse.julialang.org/c/domain/diffeq"),
        ],
    },
    "金融数学": {
        "video": [
            ("MIT OCW 18.S096 金融数学", "https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/"),
            ("Quantopian Lectures", "https://www.quantopian.com/lectures"),
            ("Wolfram 量化金融", "https://www.wolfram.com/wolfram-u/"),
        ],
        "paper": [
            ("Black-Scholes 1973 原始论文", "https://www.cs.princeton.edu/courses/archive/fall09/cos323/papers/black_scholes73.pdf"),
            ("Li 2000 Copula 论文", "https://doi.org/10.1142/9789812702629_0009"),
            ("Markowitz 1952 投资组合", "https://www.math.hkust.edu.hk/~maykwok/courses/ma362/07F/markowitz_JF.pdf"),
        ],
        "code": [
            ("QuantLib", "https://www.quantlib.org/"),
            ("zipline 量化回测", "https://zipline.io/"),
            ("yfinance 股票数据", "https://github.com/ranaroussi/yfinance"),
        ],
        "lean": [
            ("Mathlib.Probability.Stochastic", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Quant Stack Exchange", "https://quant.stackexchange.com/"),
            ("r/algotrading", "https://www.reddit.com/r/algotrading/"),
            ("Wilmott Forum", "https://forum.wilmott.com/"),
        ],
    },
    "数论": {
        "video": [
            ("Numberphile", "https://www.youtube.com/@numberphile"),
            ("MIT OCW 18.781 数论", "https://ocw.mit.edu/courses/18-781-theory-of-numbers-spring-2012/"),
            ("3Blue1Brown 模形式", "https://www.youtube.com/watch?v=KTJ4zr1HGj0"),
        ],
        "paper": [
            ("Wiles 1995 Fermat 大定理", "https://doi.org/10.2307/2118559"),
            ("Riemann 1859 原始论文", "https://www.claymath.org/sites/default/files/riemann1859.pdf"),
        ],
        "code": [
            ("SymPy Number Theory", "https://docs.sympy.org/latest/modules/ntheory.html"),
            ("SageMath 数论", "https://doc.sagemath.org/"),
            ("PARI/GP", "https://pari.math.u-bordeaux.fr/"),
        ],
        "lean": [
            ("Mathlib.NumberTheory", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/NumberTheory/"),
        ],
        "community": [
            ("Math StackExchange [number-theory]", "https://math.stackexchange.com/questions/tagged/number-theory"),
            ("MathOverflow 数论", "https://mathoverflow.net/questions/tagged/nt.number-theory"),
            ("LMFDB 数据库", "https://www.lmfdb.org/"),
        ],
    },
    "几何·拓扑": {
        "video": [
            ("3Blue1Brown 拓扑", "https://www.youtube.com/watch?v=AmgkSdhK4K8"),
            ("MIT OCW 18.901 拓扑", "https://ocw.mit.edu/courses/18-901-introduction-to-topology-fall-2004/"),
            ("Niles Johnson 代数拓扑", "https://www.youtube.com/playlist?list=PLOROt7P3ddxavPYHKZ4mIAzL4jibWm2kR"),
        ],
        "paper": [
            ("Poincaré 1895 原始论文", "https://www.maths.ed.ac.uk/~v1ranick/papers/poincare1895.pdf"),
        ],
        "code": [
            ("GUDHI TDA C++", "https://gudhi.inria.fr/"),
            ("scikit-tda", "https://scikit-tda.org/"),
            ("ripser", "https://github.com/Ripser/ripser"),
        ],
        "lean": [
            ("Mathlib.Topology.Basic", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Basic.html"),
        ],
        "community": [
            ("Math StackExchange [general-topology]", "https://math.stackexchange.com/questions/tagged/general-topology"),
            ("MathOverflow [at.algebraic-topology]", "https://mathoverflow.net/questions/tagged/at.algebraic-topology"),
        ],
    },
    "代数·抽象": {
        "video": [
            ("Benedict Gross Harvard Abstract Algebra", "https://www.youtube.com/playlist?list=PLelIK3uylPMGzSVu8gXvWiNYu01N8E1Vv"),
            ("MIT OCW 18.701 抽代", "https://ocw.mit.edu/courses/18-701-algebra-i-fall-2010/"),
        ],
        "paper": [
            ("Galois 1832 原始论文", "https://www-history.mcs.st-andrews.ac.uk/Extras/Galois_1832.pdf"),
        ],
        "code": [
            ("SageMath 代数", "https://doc.sagemath.org/"),
            ("GAP 群论", "https://www.gap-system.org/"),
            ("SymPy 抽代", "https://docs.sympy.org/latest/modules/polys/index.html"),
        ],
        "lean": [
            ("Mathlib.Algebra.Group", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Group/"),
            ("Mathlib.Algebra.Ring", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Algebra/Ring/"),
        ],
        "community": [
            ("Math StackExchange [abstract-algebra]", "https://math.stackexchange.com/questions/tagged/abstract-algebra"),
            ("GAP Forum", "https://www.gap-system.org/Contacts/Forum/forum.html"),
        ],
    },
    "几何·微分/黎曼": {
        "video": [
            ("Frederic Schuller 几何讲座", "https://www.youtube.com/playlist?list=PLPH7f_7ZlzxTi6kS4vCmv4ZKm9J8_jfMw"),
            ("MIT OCW 18.950 微分几何", "https://ocw.mit.edu/courses/18-950-differential-geometry-fall-2008/"),
        ],
        "paper": [
            ("Einstein 1915 广义相对论", "https://einsteinpapers.press.princeton.edu/"),
            ("Atiyah-Singer 1963 指标定理", "https://www.maths.ed.ac.uk/~v1ranick/papers/atiyahsinger.pdf"),
        ],
        "code": [
            ("SageManifolds", "https://sagemanifolds.obspm.fr/"),
            ("sympy.diffgeom", "https://docs.sympy.org/latest/modules/diffgeom.html"),
        ],
        "lean": [
            ("Mathlib.Geometry.Manifold", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Geometry/Manifold/"),
        ],
        "community": [
            ("MathOverflow [dg.differential-geometry]", "https://mathoverflow.net/questions/tagged/dg.differential-geometry"),
        ],
    },
    "分析·泛函": {
        "video": [
            ("MIT OCW 18.102 泛函分析", "https://ocw.mit.edu/courses/18-102-introduction-to-functional-analysis-spring-2021/"),
            ("Frederic Schuller 量子力学几何讲座", "https://www.youtube.com/@FSchuller"),
        ],
        "paper": [
            ("Banach 1932《线性算子理论》", "https://www.maths.ed.ac.uk/~v1ranick/papers/banach.pdf"),
            ("Gelfand 1941 赋范环", "https://www.maths.ed.ac.uk/~v1ranick/papers/gelfand2.pdf"),
        ],
        "code": [
            ("scipy.linalg 泛函", "https://docs.scipy.org/doc/scipy/reference/linalg.html"),
        ],
        "lean": [
            ("Mathlib.Analysis.Normed.Operator", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("MathOverflow [fa.functional-analysis]", "https://mathoverflow.net/questions/tagged/fa.functional-analysis"),
        ],
    },
    "分析·调和/小波": {
        "video": [
            ("3Blue1Brown 傅里叶变换", "https://www.youtube.com/watch?v=spUNpyF58BY"),
            ("Steve Brunton 傅里叶", "https://www.youtube.com/@Eigensteve"),
        ],
        "paper": [
            ("Fourier 1822《热的解析理论》", "https://gallica.bnf.fr/"),
            ("Daubechies 1988 小波", "https://doi.org/10.1109/ICASSP.1988.196718"),
        ],
        "code": [
            ("PyWavelets", "https://pywavelets.readthedocs.io/"),
            ("scipy.fft", "https://docs.scipy.org/doc/scipy/reference/fft.html"),
            ("FFTW", "https://www.fftw.org/"),
        ],
        "lean": [
            ("Mathlib.Analysis.Fourier", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("MathOverflow [ca.classical-analysis]", "https://mathoverflow.net/questions/tagged/ca.classical-analysis"),
            ("DSP Stack Exchange", "https://dsp.stackexchange.com/"),
        ],
    },
    "组合/图论": {
        "video": [
            ("MIT OCW 18.217 组合论", "https://ocw.mit.edu/courses/18-217-combinatorial-theory-fall-2019/"),
            ("NPTEL 图论", "https://nptel.ac.in/courses/111106064"),
        ],
        "paper": [
            ("Erdős-Rényi 1960 随机图", "https://doi.org/10.2307/3611648"),
            ("Page-Brin 1998 PageRank", "http://ilpubs.stanford.edu:8090/422/"),
        ],
        "code": [
            ("NetworkX", "https://networkx.org/"),
            ("igraph", "https://igraph.org/"),
            ("SageMath 组合", "https://doc.sagemath.org/"),
        ],
        "lean": [
            ("Mathlib.Combinatorics.SimpleGraph", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Combinatorics/SimpleGraph/"),
        ],
        "community": [
            ("MathOverflow [co.combinatorics]", "https://mathoverflow.net/questions/tagged/co.combinatorics"),
        ],
    },
    "逻辑/基础/集合/范畴": {
        "video": [
            ("MIT OCW 18.100 数理逻辑", "https://ocw.mit.edu/courses/18-100-mathematical-reasoning-and-proof-fall-2024/"),
            ("Bartosz Milewski 范畴论", "https://www.youtube.com/@BartoszMilewski"),
            ("Type Theory HoTT", "https://www.youtube.com/@HomotopyTypeTheory"),
        ],
        "paper": [
            ("Gödel 1931 不完备定理", "https://www.maths.ed.ac.uk/~v1ranick/papers/godel.pdf"),
            ("Mac Lane 1945 范畴论", "https://www.maths.ed.ac.uk/~v1ranick/papers/em-category.pdf"),
            ("Voevodsky HoTT Book", "https://homotopytypetheory.org/book/"),
        ],
        "code": [
            ("Lean 4", "https://leanprover.github.io/"),
            ("Coq", "https://coq.inria.fr/"),
            ("Agda", "https://wiki.portal.chalmers.se/agda/"),
        ],
        "lean": [
            ("Mathlib.CategoryTheory", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/"),
            ("Mathlib.Logic", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Logic/"),
        ],
        "community": [
            ("MathOverflow [lo.logic]", "https://mathoverflow.net/questions/tagged/lo.logic"),
            ("Lean Zulip", "https://leanprover.zulipchat.com/"),
            ("HoTT Google Group", "https://groups.google.com/forum/#!forum/homotopytypetheory"),
        ],
    },
    "优化/变分/控制": {
        "video": [
            ("Stanford EE364a Convex Optimization (Boyd)", "https://web.stanford.edu/class/ee364a/"),
            ("Stephen Boyd 凸优化矩阵法", "https://www.youtube.com/@StephenLBoyd"),
        ],
        "paper": [
            ("Nesterov 1983 加速梯度", "https://doi.org/10.1007/BF02568734"),
            ("Kingma-Ba 2014 Adam", "https://arxiv.org/abs/1412.6980"),
        ],
        "code": [
            ("cvxpy", "https://www.cvxpy.org/"),
            ("scipy.optimize", "https://docs.scipy.org/doc/scipy/reference/optimize.html"),
            ("JuMP.jl", "https://jump.dev/"),
        ],
        "lean": [
            ("Mathlib.Analysis.Convex", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("CVXPY Google Group", "https://groups.google.com/g/cvxpy"),
            ("Optimization Stack Exchange", "https://or.stackexchange.com/"),
        ],
    },
    "数值/计算/算法": {
        "video": [
            ("MIT OCW 18.330 数值分析", "https://ocw.mit.edu/courses/18-330-introduction-to-numerical-analysis-spring-2012/"),
            ("Steve Brunton 数值方法", "https://www.youtube.com/@Eigensteve"),
        ],
        "paper": [
            ("Henrici 1964《数值分析要素》", "https://doi.org/10.1007/978-1-4899-6277-4"),
            ("Trefethen 1996《数值线性代数》", "https://www.cs.cornell.edu/courses/cs4220/2021sp/"),
        ],
        "code": [
            ("NumPy", "https://numpy.org/"),
            ("SciPy", "https://scipy.org/"),
            ("PyTorch", "https://pytorch.org/"),
        ],
        "lean": [
            ("Mathlib.Numerics", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("NumPy Discussions", "https://github.com/numpy/numpy/discussions"),
            ("SciPy User Group", "https://scipy.org/"),
        ],
    },
    "信息/编码/密码": {
        "video": [
            ("MIT OCW 6.441 信息论", "https://ocw.mit.edu/courses/6-441-information-theory-spring-2016/"),
            ("Christof Paar 密码学", "https://www.youtube.com/playlist?list=PL2C8F6F1D3F5C9E6F"),
        ],
        "paper": [
            ("Shannon 1948 信息论", "https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf"),
            ("Diffie-Hellman 1976", "https://ee.stanford.edu/~hellman/publications/24.pdf"),
            ("Rivest-Shamir-Adleman 1978 RSA", "https://people.csail.mit.edu/rivest/Rsapaper.pdf"),
        ],
        "code": [
            ("PyCryptodome", "https://pycryptodome.com/"),
            ("cryptography Python", "https://cryptography.io/"),
            ("OpenSSL", "https://www.openssl.org/"),
        ],
        "lean": [
            ("Mathlib.InformationTheory", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Crypto Stack Exchange", "https://crypto.stackexchange.com/"),
            ("IACR ePrint", "https://eprint.iacr.org/"),
        ],
    },
    "数学物理": {
        "video": [
            ("Frederic Schuller 几何 + 物理", "https://www.youtube.com/@FSchuller"),
            ("MIT OCW 8.09 经典力学", "https://ocw.mit.edu/courses/8-09-classical-mechanics-iii-fall-2014/"),
            ("Perimeter Institute 讲座", "https://www.perimeterinstitute.ca/training/perimeter-scholars-international/psi-lectures"),
        ],
        "paper": [
            ("Arnold 1989 经典力学", "https://link.springer.com/book/10.1007/978-1-4757-2063-0"),
            ("Atiyah 1988 几何 + 物理", "https://www.maths.ed.ac.uk/~v1ranick/papers/atiyah2.pdf"),
        ],
        "code": [
            ("SageManifolds", "https://sagemanifolds.obspm.fr/"),
            ("SymPy 物理", "https://docs.sympy.org/latest/modules/physics/index.html"),
        ],
        "lean": [
            ("Mathlib.Geometry.Differential", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Physics Stack Exchange", "https://physics.stackexchange.com/"),
            ("MathOverflow [math-ph]", "https://mathoverflow.net/questions/tagged/math-ph"),
        ],
    },
    "概率·随机过程": {
        "video": [
            ("MIT OCW 6.262 随机过程", "https://ocw.mit.edu/courses/6-262-discrete-stochastic-processes-spring-2011/"),
            ("Sidney Resfield Stochastic", "https://www.youtube.com/"),
        ],
        "paper": [
            ("Itô 1944 随机积分", "https://www.jstage.jst.go.jp/article/jmj1948/3/1/3_1_55/_article"),
            ("Karatzas-Shreve 1988", "https://link.springer.com/book/10.1007/978-1-4612-0949-2"),
        ],
        "code": [
            ("RandomState numpy", "https://numpy.org/doc/stable/reference/random/"),
            ("stochastic Python", "https://stochastic.readthedocs.io/"),
            ("QuantLib 随机过程", "https://www.quantlib.org/"),
        ],
        "lean": [
            ("Mathlib.Probability.Stochastic", "https://leanprover-community.github.io/mathlib4_docs/"),
        ],
        "community": [
            ("Math StackExchange [stochastic-processes]", "https://math.stackexchange.com/questions/tagged/stochastic-processes"),
        ],
    },
    "分析·实分析/测度": {
        "video": [
            ("MIT OCW 18.100C 实分析", "https://ocw.mit.edu/courses/18-100c-real-analysis-fall-2012/"),
            ("MathTheBeautiful 实分析", "https://www.youtube.com/"),
        ],
        "paper": [
            ("Lebesgue 1902 论文", "https://www.numdam.org/item/AFST_1902_1_8_4_S4_0/"),
            ("Carathéodory 1914 测度", "https://eudml.org/doc/145419"),
        ],
        "code": [
            ("SymPy Integration", "https://docs.sympy.org/latest/modules/integrals/integrals.html"),
            ("mpmath 高精度", "https://mpmath.org/"),
        ],
        "lean": [
            ("Mathlib.MeasureTheory", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/MeasureTheory/"),
        ],
        "community": [
            ("Math StackExchange [real-analysis]", "https://math.stackexchange.com/questions/tagged/real-analysis"),
            ("MathOverflow [ca.analysis-and-odes]", "https://mathoverflow.net/questions/tagged/ca.analysis-and-odes"),
        ],
    },
    "分析·复分析": {
        "video": [
            ("MIT OCW 18.04 复变函数", "https://ocw.mit.edu/courses/18-04-complex-variables-with-applications-fall-1999/"),
            ("Wesleyan 复分析", "https://www.youtube.com/playlist?list=PLi01XoE8jYoi6q7z5zU5Vb5fX_KfB6X2r"),
        ],
        "paper": [
            ("Cauchy 1825 积分定理", "https://gallica.bnf.fr/"),
            ("Riemann 1851 复分析博士论文", "https://www.maths.ed.ac.uk/~v1ranick/papers/riemann1851.pdf"),
        ],
        "code": [
            ("mpmath 复数", "https://mpmath.org/"),
            ("SymPy 复分析", "https://docs.sympy.org/latest/modules/functions/elementary.html"),
        ],
        "lean": [
            ("Mathlib.Analysis.Complex", "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Complex/"),
        ],
        "community": [
            ("Math StackExchange [complex-analysis]", "https://math.stackexchange.com/questions/tagged/complex-analysis"),
        ],
    },
    "代数·线性": {
        "video": [
            ("3Blue1Brown 线性代数", "https://www.3blue1brown.com/topics/linear-algebra"),
            ("MIT OCW 18.06 Strang", "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/"),
        ],
        "paper": [],
        "code": [
            ("numpy.linalg", "https://numpy.org/doc/stable/reference/routines.linalg.html"),
            ("Eigen", "https://eigen.tuxfamily.org/"),
        ],
        "lean": [],
        "community": [],
    },
    "数学史/科普/方法论": {
        "video": [
            ("Numberphile", "https://www.youtube.com/@numberphile"),
            ("Mathologer", "https://www.youtube.com/@Mathologer"),
            ("MathAntics", "https://www.youtube.com/@mathantics"),
            ("3Blue1Brown", "https://www.3blue1brown.com/"),
        ],
        "paper": [
            ("Tao《What is good mathematics?》", "https://arxiv.org/abs/0707.3264"),
            ("Wigner 1960 不合理有效性", "https://www.maths.ed.ac.uk/~v1ranick/papers/wigner.pdf"),
        ],
        "code": [],
        "lean": [],
        "community": [
            ("Math StackExchange", "https://math.stackexchange.com/"),
            ("r/math", "https://www.reddit.com/r/math/"),
            ("Quanta Magazine", "https://www.quantamagazine.org/mathematics/"),
        ],
    },
    "其他": {
        "video": [("Khan Academy", "https://www.khanacademy.org/math")],
        "paper": [],
        "code": [],
        "lean": [],
        "community": [("Math StackExchange", "https://math.stackexchange.com/")],
    },
}

# === 三角色建议 ===
THEME_ROLES = {
    "分析·微积分": {"教材": "阶段1-2 主线", "工程师": "数值分析基础", "研究员": "分析方向"},
    "代数·线性": {"教材": "阶段1 主线 + 阶段2 工具书", "工程师": "ML/PCA/SVD 必备", "研究员": "线性代数研究"},
    "概率·统计": {"教材": "阶段1-2 主线", "工程师": "AI/量化/数据科学", "研究员": "概率论研究"},
    "动力系统/ODE/PDE": {"教材": "阶段2 应用", "工程师": "气候/疫情/电网", "研究员": "动力系统研究"},
    "金融数学": {"教材": "阶段3 量化方向", "工程师": "量化基金必备", "研究员": "金融数学研究"},
    "数论": {"教材": "阶段3 数论方向", "工程师": "密码学实现", "研究员": "数论研究"},
    "几何·拓扑": {"教材": "阶段2 拓扑主线", "工程师": "TDA 数据分析", "研究员": "拓扑研究"},
    "代数·抽象": {"教材": "阶段2 抽代主线", "工程师": "抽象建模", "研究员": "代数研究"},
    "几何·微分/黎曼": {"教材": "阶段3 几何", "工程师": "广义相对论工程", "研究员": "几何研究"},
    "分析·泛函": {"教材": "阶段2 泛函", "工程师": "量子/核方法 ML", "研究员": "泛函研究"},
    "分析·调和/小波": {"教材": "阶段2 调和", "工程师": "JPEG/MP3/5G 必备", "研究员": "调和分析研究"},
    "组合/图论": {"教材": "阶段1 离散", "工程师": "PageRank/物流", "研究员": "组合研究"},
    "逻辑/基础/集合/范畴": {"教材": "阶段2 元数学", "工程师": "Lean/Coq 验证", "研究员": "数学基础研究"},
    "优化/变分/控制": {"教材": "阶段2-3 优化", "工程师": "ML/航天控制", "研究员": "优化研究"},
    "数值/计算/算法": {"教材": "阶段2 数值", "工程师": "GPU/科学计算", "研究员": "数值研究"},
    "信息/编码/密码": {"教材": "阶段3 信息论", "工程师": "HTTPS/比特币", "研究员": "信息论研究"},
    "数学物理": {"教材": "阶段3 物理", "工程师": "核聚变/量子", "研究员": "数学物理研究"},
    "概率·随机过程": {"教材": "阶段3 随机", "工程师": "量化/扩散模型", "研究员": "随机研究"},
    "分析·实分析/测度": {"教材": "阶段2 测度", "工程师": "概率严格化", "研究员": "测度研究"},
    "分析·复分析": {"教材": "阶段2 复分析", "工程师": "信号处理", "研究员": "复分析研究"},
    "数学史/科普/方法论": {"教材": "阶段0-1 热身", "工程师": "灵感来源", "研究员": "方法论"},
    "其他": {"教材": "通用", "工程师": "通用", "研究员": "通用"},
}


def detect_theme(name):
    for theme, kws in {
        "分析·微积分": ["微积分", "Calculus", "数学分析", "Mathematical Analysis"],
        "分析·实分析/测度": ["实分析", "Real Analysis", "测度", "Measure"],
        "分析·复分析": ["复分析", "复变", "Complex"],
        "分析·泛函": ["泛函", "Functional", "Banach", "Hilbert", "Operator"],
        "分析·调和/小波": ["调和", "Fourier", "小波", "Harmonic"],
        "代数·线性": ["线性代数", "Linear Algebra", "矩阵", "Matrix"],
        "代数·抽象": ["抽象代数", "Abstract Algebra", "代数", "Algebra"],
        "代数·群论": ["群论", "Group"],
        "几何·拓扑": ["拓扑", "Topology", "流形"],
        "几何·微分/黎曼": ["微分几何", "黎曼", "Riemannian"],
        "几何·代数": ["代数几何", "Algebraic Geometry"],
        "概率·统计": ["概率", "Probability", "统计", "Statistics"],
        "概率·随机过程": ["随机", "Stochastic", "Brownian"],
        "数论": ["数论", "Number Theory"],
        "组合/图论": ["组合", "Combinator", "图论", "Graph"],
        "逻辑/基础/集合/范畴": ["逻辑", "Logic", "集合", "范畴"],
        "动力系统/ODE/PDE": ["微分方程", "动力系统", "反应扩散"],
        "金融数学": ["金融", "Financial"],
        "数学史/科普/方法论": ["史", "故事", "游戏"],
        "数学物理": ["力学", "Mechanic", "物理", "Physic"],
        "信息/编码/密码": ["信息", "Information", "编码", "Coding", "密码"],
        "优化/变分/控制": ["优化", "Optimi", "控制", "Control"],
        "数值/计算/算法": ["数值", "Numerical", "算法", "Algorithm"],
    }.items():
        for kw in kws:
            if kw in name: return theme
    return "其他"


def render_md(book_md_path):
    name = book_md_path.stem
    series = book_md_path.parent.name
    theme = detect_theme(name)
    resources = THEME_RESOURCES.get(theme, THEME_RESOURCES["其他"])
    roles = THEME_ROLES.get(theme, THEME_ROLES["其他"])
    
    L = []
    L.append(f"# 三角色资源档案：{name}\n")
    L.append(f"> 自动生成 · 丛书：{series} · 主题：**{theme}**\n")
    L.append("")
    
    # 三角色定位
    L.append("## 🎭 三角色定位\n")
    L.append(f"| 角色 | 本书定位 |")
    L.append(f"|------|---------|")
    L.append(f"| 📘 **教材学习者** | {roles['教材']} |")
    L.append(f"| 🔧 **工程师实战** | {roles['工程师']} |")
    L.append(f"| 🔬 **研究员学术** | {roles['研究员']} |")
    L.append("")
    
    # 网络资源
    L.append("## 🌐 网络资源（按角色优先级）\n")
    
    L.append(f"### 📘 教材优先（建立直觉）\n")
    L.append("**视频课程**：")
    for title, url in resources["video"][:3]:
        L.append(f"- [{title}]({url})")
    L.append("")
    
    L.append("**经典论文/参考**：")
    for title, url in resources["paper"][:3]:
        L.append(f"- [{title}]({url})")
    L.append("")
    
    L.append(f"### 🔧 工程师优先（实战代码）\n")
    L.append("**Python/代码实现**：")
    for title, url in resources["code"][:3]:
        L.append(f"- [{title}]({url})")
    L.append("")
    
    L.append(f"### 🔬 研究员优先（形式化 + 社区）\n")
    L.append("**Lean 形式化**：")
    for title, url in resources["lean"][:3]:
        L.append(f"- [{title}]({url})")
    L.append("")
    
    L.append("**学术社区**：")
    for title, url in resources["community"][:3]:
        L.append(f"- [{title}]({url})")
    L.append("")
    
    # 综合学习路径
    L.append("## 🎯 综合学习路径\n")
    L.append(f"### 📘 教材路径（系统建立成熟度）")
    L.append(f"1. 看 1 个 3Blue1Brown 视频建立直觉")
    L.append(f"2. 精读书中核心章节")
    L.append(f"3. 用 SymPy/numpy 跑一遍")
    L.append(f"4. 写笔记")
    L.append(f"5. 跨书对照（参考 09-crosstext）")
    L.append("")
    
    L.append(f"### 🔧 工程师路径（解决具体问题）")
    L.append(f"1. 识别项目需求")
    L.append(f"2. 查书中公式/算法")
    L.append(f"3. GitHub 找开源实现")
    L.append(f"4. 真实数据验证")
    L.append(f"5. 查失败案例档案避坑")
    L.append("")
    
    L.append(f"### 🔬 研究员路径（推进前沿）")
    L.append(f"1. 跨书追踪同一概念")
    L.append(f"2. arXiv 看最新论文")
    L.append(f"3. Lean 形式化")
    L.append(f"4. MathOverflow 提问")
    L.append(f"5. 写论文")
    L.append("")
    
    # 接入
    L.append("## 📐 接入 math-expert-pro 13 目录\n")
    L.append(f"- 主题：{theme}")
    L.append(f"- 配套：[书籍索引](../书籍索引/{series}/{name}.md)")
    L.append(f"- 配套：[书籍深度分析](../书籍深度分析/{series}/{name}.md)")
    L.append(f"- 配套：[主题深度报告](../书籍索引/主题深度报告-{theme.split('/')[0]}.md)")
    L.append(f"- 配套：[30 真实系统映射](../书籍索引/475书-30真实系统-映射.md)")
    L.append(f"- 配套：[10 失败案例档案](../失败案例档案/)")
    L.append("")
    
    return "\n".join(L)


def process_one(args):
    book_md_path_str, output_dir_str = args
    book_md_path = Path(book_md_path_str)
    output_dir = Path(output_dir_str)
    out_path = output_dir / (book_md_path.stem + ".md")
    if out_path.exists():
        return ("skip", book_md_path.name)
    try:
        md = render_md(book_md_path)
        out_path.write_text(md, encoding="utf-8")
        return ("ok", book_md_path.name)
    except Exception as e:
        return ("error", book_md_path.name, str(e)[:60])


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    
    if args.force:
        for d in OUTPUT_ROOT.iterdir():
            if d.is_dir():
                for f in d.glob("*.md"): f.unlink()
        print("🧹 清空")
    
    tasks = []
    for series_dir in INDEX_ROOT.iterdir():
        if not series_dir.is_dir(): continue
        out_series = OUTPUT_ROOT / series_dir.name
        out_series.mkdir(exist_ok=True)
        for md in sorted(series_dir.glob("*.md")):
            tasks.append((str(md), str(out_series)))
    
    print(f"共 {len(tasks)} 本，{args.workers} 进程")
    
    ok, skip, err = 0, 0, 0
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process_one, t): t for t in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            r = fut.result()
            if r[0] == "ok": ok += 1
            elif r[0] == "skip": skip += 1
            else: err += 1
            if i % 100 == 0:
                print(f"  [{i}/{len(tasks)}] ✅ {ok} / ⏭️ {skip} / ❌ {err}")
    
    print(f"\n✅ 完成：{ok} ok / {skip} skip / {err} err")


if __name__ == "__main__":
    main()
