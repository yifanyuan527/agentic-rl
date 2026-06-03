# Agentic RL 中文调研报告 PPT 草稿

> 版本：2026-06-03  
> 形式：30 页 PPT 草稿；传统 RL 与 LLM RL 仅作为引入，主体聚焦 Agentic RL 的 reward / credit assignment / planning / tool / memory / reasoning / self-improvement。

## Slide 01｜标题：Agentic RL 调研

**正文要点**
- 主题：从 LLM 对齐到长期自主决策的 Reward、Credit Assignment 与方法图谱
- 核心问题：Agent 为什么需要 RL？Agentic RL 与传统 RL / LLM RL 的区别在哪里？
- 重点：reward 机制、长程信用分配、规划 / 工具 / 记忆 / 推理模块如何被 RL 化

**图表建议**
- 背景图：LLM → Agent → Environment → Feedback → RL Update 的闭环。

**讲稿提示**
- 开场强调：本报告不是 RL 发展史，而是以 Agentic RL 为主体，传统 RL 与 LLM RL 只是对照组。

## Slide 02｜Executive Summary：一句话结论

**正文要点**
- Agentic RL 的核心不是让 LLM 多调用工具，而是训练 LLM agent 在动态环境中做长期、多步、可反馈的决策。
- 与普通 LLM RL 相比，Agentic RL 优化对象从 response 变成 trajectory。
- 当前最大瓶颈是 reward 与 credit assignment：知道一条轨迹成功，不等于知道哪一步应该被强化。
- 主流研究正在从 outcome reward 走向 verifier-guided process reward、critic-assisted credit assignment、counterfactual attribution 与 hierarchical reward。

**图表建议**
- 放一条主线：Response-level RL → Trajectory-level RL → Module-level / Step-level Credit Assignment。

**参考**
- The Landscape of Agentic Reinforcement Learning for LLMs: A Survey, arXiv:2509.02547, https://arxiv.org/abs/2509.02547
- From Reasoning to Agentic: Credit Assignment in RL for LLMs, arXiv:2604.09459, https://arxiv.org/abs/2604.09459

## Slide 03｜从传统 RL 到 Agentic RL：为什么不是简单换个模型？

**正文要点**
- 传统 RL：在相对明确的状态、动作、奖励定义下学习控制策略。
- LLM RL：主要优化 prompt → response 的输出质量，常见 reward 来自偏好、规则或可验证答案。
- Agentic RL：优化多轮环境交互轨迹，动作包含规划、工具调用、搜索、代码执行、记忆读写、对话与协作。
- 范式变化：从 single-step / short-horizon text optimization 走向 long-horizon interactive decision making。

**图表建议**
- 三栏对比图：Traditional RL / LLM RL / Agentic RL。

**参考**
- The Landscape of Agentic Reinforcement Learning for LLMs: A Survey, arXiv:2509.02547。

## Slide 04｜三种范式核心对比

**正文要点**
- 传统 RL 的 action 通常是环境动作；LLM RL 的 action 常被视为 token 或完整回答；Agentic RL 的 action 是复合行为。
- 传统 RL 的 reward 多来自环境；LLM RL 多来自偏好模型或 verifier；Agentic RL 需要同时考虑任务成功、过程质量、成本和安全。
- Agentic RL 的 state 包含 observation、历史上下文、memory、tool results、plan 与隐含 belief，天然更接近 POMDP。
- Agentic RL 的难点不是有没有 RL 算法，而是如何定义可训练、可归因、可泛化的 agent 交互信号。

**图表建议**
- 表格：State / Action / Reward / Horizon / Environment / Main Challenge。

## Slide 05｜为什么 Agent 需要 RL？

**正文要点**
- Agent 的任务天然是 sequential decision making：每一步都会改变后续可观测状态与可行动空间。
- 工具调用需要学习成本收益权衡：何时不用工具、何时调用、调哪个、参数怎么写、失败后如何恢复。
- 记忆模块需要学习策略：何时写、写什么、何时读、何时删除或修正。
- 规划模块需要适应反馈：计划不是一次生成后固定执行，而是要根据环境结果持续修正。
- 只靠 SFT 容易模仿成功轨迹表象，难以从失败、探索和环境反馈中持续改进。

**图表建议**
- 闭环：Goal → Plan → Act/Tool → Observe → Memory Update → Replan → Reward。

## Slide 06｜Agentic RL 的基本建模

**正文要点**
- Observation：网页状态、工具返回、代码执行结果、数据库查询、用户反馈、其他 agent 消息。
- Internal State / Belief：历史上下文、working memory、long-term memory、当前 plan、失败反思、检索内容。
- Action：自然语言回复、工具调用、API 参数、代码 patch、搜索 query、memory 写入、子任务分配。
- Reward：最终成功、子目标完成、过程质量、工具成本、时间成本、安全约束、用户满意度。
- Policy：不仅是 base LLM，也包括 planner、tool router、memory manager、verifier、reflection loop 等 scaffold。

**图表建议**
- POMDP + Agent Scaffold 框图。

## Slide 07｜哪些传统 / LLM RL 方法可以保留？

**正文要点**
- Policy optimization：PPO、REINFORCE、GRPO、RLOO 等可迁移到轨迹级优化。
- Reward shaping：final reward 太稀疏，必须补充 step reward、turn reward、process reward、cost penalty。
- Hierarchical RL：Agent 天然分层，适合用 subgoal、option、skill、planner-executor 结构描述。
- Offline / imitation：专家轨迹、人类操作日志、成功 agent traces 可用于 warm start 或偏好数据。
- Critic / value model：可以尝试估计每一步状态或动作的长期价值，缓解高方差。

**图表建议**
- “可迁移方法”五宫格。

## Slide 08｜哪些地方会出问题？

**正文要点**
- State 不干净：环境、长上下文、记忆、工具输出、隐式计划混合在一起。
- Action 空间巨大：一个 action 可能是一段代码、一次网页操作、一次 API 调用或一次 memory 写入。
- Reward 稀疏且延迟：几十步之后才知道任务成败。
- Credit assignment 极难：成功轨迹里可能有无效步骤，失败轨迹里也可能有关键探索。
- 环境非平稳：网页、API、用户反馈和外部工具都可能变化，复现与离线训练困难。

**图表建议**
- “保留 vs 失效”对照表。

## Slide 09｜报告核心：Reward 与 Credit Assignment

**正文要点**
- Agentic RL 的 reward 困境：我们优化的是整条 trajectory，但真正需要学习的是每一步 action 的选择。
- Trajectory 好，不代表每一步都好；trajectory 坏，也不代表每一步都坏。
- 关键问题：如何把最终成功或失败分配给 planning、tool use、memory、reasoning、reflection 等不同模块？
- 当前没有通用解，主流方法只能从不同角度缓解稀疏 reward 与长程信用分配。

**图表建议**
- 轨迹示例：Search → Tool → Wrong Read → Replan → Memory → Success，并标注“哪一步该奖励？”

**参考**
- From Reasoning to Agentic: Credit Assignment in RL for LLMs, arXiv:2604.09459。
- RAGEN, arXiv:2504.20073, https://arxiv.org/abs/2504.20073

## Slide 10｜Reward 层次一：Outcome / Trajectory Reward

**正文要点**
- 定义：只根据整条轨迹最终结果给奖励，例如成功 +1、失败 0 或 -1。
- 优点：客观、简单、易规模化，适合代码测试、数学答案、网页目标状态、游戏胜负等可验证任务。
- 缺点：奖励稀疏、高方差、不能定位步骤贡献，也容易导致 benchmark overfitting 或 verifier hacking。
- 结论：trajectory-level reward 是 Agentic RL 的起点，但不是终点。

**图表建议**
- “Final Reward Only”的长轨迹图，最后一个节点有 reward，前面节点为空。

## Slide 11｜Reward 层次二：Process / Step / Turn Reward

**正文要点**
- 定义：对中间推理、计划、工具调用、搜索 query、memory 操作或每一轮 turn 给局部奖励。
- 优点：比 outcome reward 更密集，有助于长任务训练和失败定位。
- 风险：可能奖励“看起来合理”的过程，而不是真正有效的行为；也可能诱导冗长 reasoning 或形式主义计划。
- 关键要求：过程奖励最好与外部验证、状态变化或可执行检查绑定，而不是只看语言表面。

**图表建议**
- Outcome reward vs Process reward 的奖励密度对比。

**参考**
- Reinforcing Multi-Turn Reasoning in LLM Agents via Turn-Level Reward Design, arXiv:2505.11821。
- Verifiable Process Rewards for Agentic Reasoning, arXiv:2605.10325。

## Slide 12｜Verifier-based Reward：目前最可靠的来源之一

**正文要点**
- Verifier 用外部环境或规则判断结果：单元测试、数学校验、SQL 执行、网页状态、工具返回、游戏环境。
- 优点：比纯偏好模型更客观，适合规模化采样与自动评估。
- 局限：只适用于可验证任务，且 verifier 可能覆盖不全、被 hack，无法完全解释中间步骤贡献。
- 趋势：从只验证最终答案，发展到验证中间状态、局部子目标和工具调用结果。

**图表建议**
- Agent → Environment / Tool → Verifier → Reward 的闭环。

## Slide 13｜Critic / Value Model：从“整条轨迹”到“每一步价值”

**正文要点**
- 思路：训练 V(s_t) 或 Q(s_t, a_t) 估计从当前状态或动作继续执行的长期成功概率。
- 好处：理论上可以做 step-level credit assignment，降低 policy gradient 方差。
- 难点：Agentic state 包含长上下文、工具状态、记忆与隐式计划，critic 很难稳定、准确地建模。
- 实践问题：critic 可能 hallucinate value，也可能对未见环境泛化差。

**图表建议**
- 每个时间步标注 V_t / Advantage_t。

## Slide 14｜Counterfactual / Leave-one-out：更接近因果归因

**正文要点**
- 核心问题：如果去掉或替换某一步，最终结果是否变化？
- 例子：原轨迹成功；去掉某次工具调用后失败，则该工具调用可能是关键贡献步骤。
- 优点：比表面 process reward 更接近因果 credit assignment。
- 缺点：需要多次 rollout，成本高；开放环境可能不可复现；长轨迹组合爆炸。
- 适用：高价值任务、离线分析、诊断 reward model、训练 critic 的辅助信号。

**图表建议**
- 原轨迹 vs 替换轨迹的分叉图。

**参考**
- From Reasoning to Agentic: Credit Assignment in RL for LLMs, arXiv:2604.09459。

## Slide 15｜Hierarchical Reward：把长期任务拆成子目标

**正文要点**
- 思路：把长任务拆成 planner-level 子目标和 executor-level 行动，每个子目标有局部 reward。
- 优点：降低长程信用分配难度，符合 Agent 的自然结构。
- 例子：修复 bug 可拆成定位文件、理解失败测试、修改代码、运行验证、提交 patch。
- 难点：子目标如何自动生成？局部 reward 与最终目标是否一致？错误分解会不会误导训练？

**图表建议**
- Task → Subgoal → Action → Token 的层级树。

**参考**
- HiPER: Hierarchical RL with Explicit Credit Assignment for LLM Agents, arXiv:2602.16165。

## Slide 16｜Reward 机制小结：没有银弹，但有组合拳

**正文要点**
- Outcome reward 负责判断“最后是否成功”。
- Process / turn reward 负责提供更密集的训练信号。
- Verifier reward 负责把奖励绑定到外部事实或可执行检查。
- Critic / value model 负责估计中间状态价值。
- Counterfactual 负责更接近因果的归因诊断。
- Hierarchical reward 负责降低长任务跨度，把 credit assignment 分散到子目标层。

**图表建议**
- Reward toolbox 表格：机制 / 解决什么 / 优点 / 问题。

## Slide 17｜主流方法图谱：按 Agent 模块组织

**正文要点**
- 本报告不按算法名堆论文，而按 Agent 模块组织：planning、tool use、memory、reasoning、self-improvement、multi-agent。
- 每个模块都问四个问题：action 是什么？reward 怎么给？credit assignment 难在哪里？现有方法如何缓解？
- 这种组织方式更贴近 Agentic RL 的本质：训练整个 agent system，而不只是训练 base model。

**图表建议**
- Agent scaffold 模块图：Planner / Tool Router / Memory / Reasoner / Verifier / Executor。

**参考**
- The Landscape of Agentic Reinforcement Learning for LLMs: A Survey, arXiv:2509.02547。

## Slide 18｜RL for Planning：从静态计划到自适应重规划

**正文要点**
- Action：任务分解、子目标选择、计划粒度控制、何时重规划、何时停止。
- Reward：子目标完成率、最终任务成功、计划执行成本、重规划后是否纠错。
- 难点：计划看起来合理不等于可执行；错误计划可能在后续被修正，贡献难归因。
- 方法方向：ReAct 式 reasoning-action interleaving、tree search + verifier、planner-executor 分层训练、turn-level reward。

**图表建议**
- Plan → Act → Observe → Replan 循环。

**参考**
- ReAct: Synergizing Reasoning and Acting in Language Models, arXiv:2210.03629, https://arxiv.org/abs/2210.03629

## Slide 19｜RL for Tool Use：学会何时、如何、是否调用工具

**正文要点**
- Action：选择工具、生成参数、解释工具输出、失败重试、终止工具调用。
- Reward：最终成功、工具结果是否有效、调用成本、参数合法性、是否减少 hallucination。
- 难点：工具失败可能是坏操作，也可能提供有价值信息；无效调用和必要探索难区分。
- 方法方向：Toolformer 式自监督工具学习、ReAct 式交互轨迹、function-call 统一接口、多工具环境 RL。

**图表建议**
- Tool router 的决策树：No tool / Search / Code / DB / Browser / API。

**参考**
- Toolformer, arXiv:2302.04761, https://arxiv.org/abs/2302.04761
- AgentRL, arXiv:2510.04206, https://arxiv.org/abs/2510.04206

## Slide 20｜RL for Memory：Agentic RL 最有特色的模块之一

**正文要点**
- Action：写入 memory、检索 memory、压缩 memory、修改 memory、删除 memory、抽象为 skill。
- Reward：当前任务成功、后续任务复用收益、检索命中率、减少 token / tool cost、避免重复错误。
- 难点：memory 的收益常常延迟出现；错误 memory 会污染未来轨迹；单条 memory 对最终结果的贡献很难归因。
- 方法方向：Reflexion 的 verbal memory、Voyager 的 skill library、episodic / semantic / procedural memory policy learning。

**图表建议**
- Memory read/write/delete policy 的闭环。

**参考**
- Reflexion, arXiv:2303.11366, https://arxiv.org/abs/2303.11366
- Voyager, arXiv:2305.16291, https://arxiv.org/abs/2305.16291

## Slide 21｜Memory 的 credit assignment 为什么特别难？

**正文要点**
- 一次 memory 写入可能当前任务无用，但未来任务有用；也可能当前看起来有用，长期造成污染。
- 检索到的 memory 可能只是辅助，也可能是关键证据；很难从 final reward 直接判断。
- 错误 memory 会被反复检索，形成自我强化的错误经验。
- 需要同时优化 write policy、retrieval policy、compression policy、deletion policy 与 conflict resolution。

**图表建议**
- 时间轴：Episode 1 写入经验，Episode 5 才体现收益。

## Slide 22｜RL for Reasoning：从“会想”到“想得有用”

**正文要点**
- Action：生成 reasoning trace、选择思考深度、调用 verifier、反思错误、决定何时停止思考并行动。
- Reward：答案正确性、过程正确性、推理成本、是否产生可执行 action。
- 难点：长 reasoning 不等于好决策；process reward 可能奖励漂亮话，而不是有效 reasoning。
- 方法方向：outcome reward + process reward、verifier-guided reasoning、group comparison、reasoning-aware reward。

**图表建议**
- “Verbose reasoning” vs “actionable reasoning” 对比。

**参考**
- RAGEN, arXiv:2504.20073。

## Slide 23｜RL for Self-improvement：从失败中形成经验

**正文要点**
- Action：复盘失败、生成反思、更新策略、保存技能、设计下一次尝试。
- Reward：重试成功率、同类任务迁移、减少重复错误、技能复用率。
- 代表：Reflexion 使用语言反馈改善后续尝试；Voyager 通过技能库积累可复用能力。
- 难点：反思可能 hallucinate；错误经验可能被固化；self-improvement 可能放大 reward hacking。

**图表建议**
- Failure → Reflection → Memory / Skill → Retry → Success 的循环。

**参考**
- Reflexion, arXiv:2303.11366。
- Voyager, arXiv:2305.16291。

## Slide 24｜RL for Multi-Agent：协作中的信用分配更复杂

**正文要点**
- Action：角色分配、消息通信、任务交接、互评、冲突解决、集体决策。
- Reward：团队成功、个体贡献、通信成本、角色完成度、安全约束。
- 难点：共享 reward 下容易 free-riding；难判断哪个 agent 的哪条消息带来成功。
- 方法方向：multi-agent credit assignment、turn-level reward、role-level critic、debate / reviewer / planner-worker 结构。

**图表建议**
- Planner / Worker / Reviewer 三角色协作图。

**参考**
- LangMARL: Natural Language Multi-Agent Reinforcement Learning, arXiv:2604.00722。

## Slide 25｜代表性系统：RAGEN / StarPO

**正文要点**
- RAGEN 研究 multi-turn agent RL 中的 self-evolution，并提出 StarPO 作为 trajectory-level agent RL 框架。
- 重要发现：多轮 agent RL 可能出现 Echo Trap、reward variance cliffs 与 gradient spikes。
- RAGEN 指出：如果没有细粒度、reasoning-aware reward signals，agent 可能学到浅层策略或幻觉式 thoughts。
- 启示：Agentic RL 不能只依赖最终 reward，需要稳定训练机制、轨迹过滤、critic 和更细粒度反馈。

**图表建议**
- Training instability：reward variance cliff / gradient spike 示意图。

**参考**
- RAGEN, arXiv:2504.20073。

## Slide 26｜代表性系统：AgentGym-RL

**正文要点**
- AgentGym-RL 面向 long-horizon multi-turn decision making，强调统一、交互式、多环境 RL 框架。
- 系统包括 environment、agent、training module，支持多场景、多算法和多轮交互。
- 价值：把 Agentic RL 从单一任务实验推进到可复用训练基础设施。
- 局限：框架解决基础设施问题，但 reward 设计、credit assignment 与跨环境泛化仍是核心挑战。

**图表建议**
- Environment / Agent / Training 三模块架构。

**参考**
- AgentGym-RL, arXiv:2509.08755, https://arxiv.org/abs/2509.08755

## Slide 27｜代表性系统：AgentRL

**正文要点**
- AgentRL 面向 scalable multi-turn, multi-task agentic RL training。
- 系统侧：异步 generation-training pipeline、统一 function-call API、容器化环境与 centralized controller。
- 算法侧：cross-policy sampling 促进多轮探索，task advantage normalization 稳定多任务训练。
- 启示：Agentic RL 的瓶颈不只是算法，也包括环境接口、采样效率、异步训练和多任务稳定性。

**图表建议**
- Asynchronous rollout → buffer → training → updated policy 的流水线。

**参考**
- AgentRL, arXiv:2510.04206。

## Slide 28｜当前方法的共同局限

**正文要点**
- Reward 仍偏稀疏：很多任务只能验证最终结果，过程监督不足。
- Credit assignment 没有通用解：critic、process reward、counterfactual 都有成本或可靠性问题。
- 泛化不足：在特定环境 / benchmark 学到的策略未必迁移到真实任务。
- 成本高：多轮 rollout、工具调用、环境执行、反事实采样都很贵。
- 安全风险更高：agent 可以调用工具和改变环境，reward hacking 的后果比普通文本生成严重。

**图表建议**
- 五个瓶颈雷达图：Reward / Credit / Generalization / Cost / Safety。

## Slide 29｜未来方向：以 Reward 和 Credit Assignment 为中心

**正文要点**
- Verifier-grounded process reward：把过程监督绑定到可执行检查，而不是语言表面。
- Memory policy learning：系统学习 memory 的写、读、压缩、删除和冲突解决。
- Hierarchical agent training：联合训练 planner、executor、tool router、memory manager。
- Counterfactual and causal credit assignment：用反事实 rollout、hindsight analysis 和 privileged critic 做更细粒度归因。
- Safe agentic RL：把权限、成本、安全约束和审计轨迹纳入 reward 与训练环境。

**图表建议**
- 未来路线图：2024–2026 outcome RL → 2026+ module-level / causal credit assignment。

## Slide 30｜总结：Agentic RL 的核心命题

**正文要点**
- Agentic RL 的研究对象是长期交互轨迹，而不是单轮回答。
- 传统 RL 和 LLM RL 的方法可以迁移，但必须重构 state、action、reward 与 evaluation。
- Reward 机制是当前最重要的瓶颈：trajectory-level success 不足以提供 action-level learning signal。
- 主流方法正在围绕 planning、tool use、memory、reasoning、self-improvement 和 multi-agent 协作展开。
- 未来最关键的突破很可能来自可验证过程奖励、因果信用分配、模块化 agent 训练和安全约束下的在线学习。

**图表建议**
- 最终一页：Agentic RL = Trajectory Optimization + Module Learning + Credit Assignment + Safety。

