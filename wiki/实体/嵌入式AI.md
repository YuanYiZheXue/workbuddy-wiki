# 嵌入式AI

> 类型：技术领域  
> 标签：#AI #嵌入式 #边缘计算  

---

## 定义

**嵌入式AI**（Embedded AI）是指在**资源受限**的嵌入式设备上部署AI模型，实现本地推理。它介于云端AI（高算力）和纯嵌入式（无AI）之间，追求**低延迟、低功耗、高隐私**。

---

## 核心挑战

### 1. 算力约束
- **CPU**：ARM Cortex-M（< 300MHz）
- **内存**：SRAM < 1MB，Flash < 16MB
- **算力**：< 1 TOPS（vs. 云端GPU 100+ TOPS）

### 2. 功耗约束
- **电池供电**：毫瓦级功耗预算
- **散热限制**：无法主动散热

### 3. 模型精度
- **模型压缩**：量化、剪枝、蒸馏
- **精度损失**：需要在压缩率和精度间权衡

---

## 关键技术

### 1. 模型压缩
| 技术 | 原理 | 压缩率 |
|------|------|--------|
| **量化**（INT8） | FP32 → INT8 | 4x |
| **剪枝**（Pruning） | 去除冗余权重 | 2-10x |
| **知识蒸馏** | 大模型 → 小模型 | 10-100x |
| **低秩分解** | 矩阵分解 | 2-5x |

### 2. 硬件加速
- **DSP**：数字信号处理器（传统）
- **NPU**：神经网络处理器（现代）
- **FPGA**：可重构硬件加速

### 3. 推理框架
| 框架 | 适用平台 | 特点 |
|------|----------|------|
| **TensorFlow Lite** | ARM Cortex-A | 易用、生态好 |
| **NCNN** | ARM Cortex-A/M | 腾讯开源、无依赖 |
| **TFLite Micro** | Cortex-M | 无OS依赖 |
| **CMSIS-NN** | Cortex-M | ARM官方、优化好 |

---

## 典型应用场景

### 1. 智能安防
- **人脸检测**：摄像头本地识别
- **行为分析**：异常行为检测
- **优势**：无云端延迟、隐私保护

### 2. 工业物联网（IIoT）
- **预测性维护**：振动分析、温度监测
- **质量控制**：视觉检测
- **优势**：实时性、离线工作

### 3. 自动驾驶（边缘部分）
- **感知**：激光雷达点云处理
- **决策**：本地路径规划
- **优势**：低延迟（< 10ms）

### 4. 智能家居
- **语音识别**：离线唤醒词识别
- **手势识别**：本地处理
- **优势**：无网络依赖、响应快

---

## 芯片平台

| 厂商 | 芯片 | AI算力 | 功耗 |
|------|------|--------|------|
| **海思** | Hi3516DV300 | 1 TOPS | 2W |
| **瑞芯微** | RK3588 | 6 TOPS | 5W |
| **全志** | V536 | 0.5 TOPS | 1W |
| **NVIDIA** | Jetson Nano | 0.5 TOPS | 5W |
| **国产** | 地平线J5 | 128 TOPS | 10W |

---

## 与工程控制论的关联

### 1. 嵌入式控制
- **状态空间法**：嵌入式AI用于状态估计
- **稳定性**：嵌入式AI控制器的稳定性分析
- **实时性**：RTOS + AI推理的时序分析

### 2. OTA更新
- **边缘AI模型更新**：通过OTA远程更新模型
- **增量更新**：只传输模型差异部分
- **验证**：嵌入式端模型完整性校验

---

## Python实现（模型量化示例）

```python
import tensorflow as tf
import numpy as np

def quantize_model():
    """模型量化示例"""
    # 加载预训练模型
    model = tf.keras.applications.MobileNetV2(weights='imagenet')
    
    # 转换为TFLite格式
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # 启用量化
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.int8]
    
    # 提供代表性数据集（用于校准）
    def representative_dataset():
        for _ in range(100):
            data = np.random.rand(1, 224, 224, 3)
            yield [data.astype(np.float32)]
    
    converter.representative_dataset = representative_dataset
    
    # 转换
    tflite_model = converter.convert()
    
    # 保存
    with open('mobilenetv2_quant.tflite', 'wb') as f:
        f.write(tflite_model)
    
    print("量化模型大小:", len(tflite_model) / 1024, "KB")
    return tflite_model
```

---

## 相关概念

- [[边缘AI]] — 同义概念页
- [[FPGA]] — 嵌入式AI的可编程硬件平台
- [[嵌入式实时操作系统]] — 嵌入式AI的软件基础
- [[模型压缩]] — 嵌入式AI的关键技术
- [[OTA]] — 嵌入式AI模型的远程更新

---

## 参考资料

- 📚 《嵌入式机器学习》（TinyML）
- 📚 《深度学习模型压缩与加速》
- TensorFlow Lite官方文档

---

> **标注**：嵌入式AI是AI技术落地的重要方向。  
> 将AI模型部署到资源受限设备，需要算法、硬件、系统的协同优化。
