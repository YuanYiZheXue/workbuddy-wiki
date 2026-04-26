---
来源：嵌入式AI与系统集成笔记
类型：工具链
标签：#EDA #芯片设计 #国产替代
---

# EDA工具链

## 定义

EDA（Electronic Design Automation，电子设计自动化）工具链是芯片设计全流程所需的软件工具集合，覆盖从 RTL 设计到制造签核的所有环节。

## 完整 EDA 工具链（数字芯片）

```
规格定义
   ↓
RTL 设计（Verilog/VHDL）→ 仿真验证（VCS/ModelSim）
   ↓
综合（Design Compiler）→ 门级网表
   ↓
形式验证（Formality/JasperGold）
   ↓
布局布线（IC Compiler/Innovus）
   ↓
时序签核（PrimeTime）
   ↓
物理验证（Calibre/Pegasus）
   ↓
流片（Tape-out）
```

## 主要厂商与工具

| 厂商 | 工具 | 领域 |
|------|------|------|
| Cadence | Virtuoso、Genus、Innovus | 模拟/数字全流程 |
| Synopsys | Design Compiler、IC Compiler、VCS | 数字全流程 |
| 华大九天 | Empyrean Allegro、Empyrean AED | 国产替代（模拟为主） |
| Ansys | RedHawk、PowerArtist | 电源完整性、热分析 |
| Siemens EDA（原 Mentor） | Calibre、Veloce | 物理验证、硬件仿真 |

## 国产 EDA 进展

| 厂商 | 工具 | 可替代环节 |
|------|------|------------|
| 华大九天 | 模拟电路设计全流程 | 模拟电路设计（较成熟） |
| 概伦电子 | 器件建模、电路仿真 | 器件建模（达国际水平） |
| 广立微 | 良率分析、测试工具 | 制造端良率优化 |
| 国微集团 | 数字验证、FPGA 验证 | 部分验证环节 |

## 验证方法学

| 方法 | 说明 |
|------|------|
| UVM（Universal Verification Methodology） | 通用验证方法学，标准化验证流程 |
| 形式验证（Formal Verification） | 数学方法证明电路等价性 |
| 硬件仿真（Emulation） | 接近真实硬件速度的验证（Veloce、Palladium） |
| FPGA 原型验证 | 用 FPGA 实现设计，提前进行软件开发 |

## 在芯片设计中的角色

嵌入式系统工程师通常接触 EDA 工具的环节：
- **FPGA 开发**：Vivado、Quartus（Xilinx/Intel 自带）
- **PCB 设计**：Altium Designer、Cadence Allegro
- **芯片选型**：在阅读数据手册时了解芯片的 EDA 流程背景

## 相关概念

- [[FPGA]]
- [[ASIC]]
- [[国产芯片替代]]

## 参考资料

- [[2026-04-26 嵌入式AI与系统集成]]
- [[📚 国产EDA]]

## 最后更新

2026-04-26
