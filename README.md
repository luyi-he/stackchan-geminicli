# Stack-chan Gemini CLI Integration Project

这个项目能让你的 Stack-chan 机器人成为 Gemini CLI 的“物理分身”。每当 AI 需要审批、任务完成或运行报错时，机器人会通过动作、表情和语音（Edge TTS）为你提供实时反馈。

## 解决刚才发现的两个 Bug

### 1. 审批没有触发响应
刚才没有触发响应是因为**我还没有把自动触发规则写入我的“长期记忆”中**。在此次计划执行阶段，我将会：
*   修改 `C:\Users\heluy\.gemini\tmp\heluy\memory\MEMORY.md`（或 `C:\Users\heluy\.gemini\GEMINI.md`），写入强制规则。
*   规则内容：每次调用 `ask_user` 或 `exit_plan_mode` 前，必须先运行 `uv run python C:\Users\heluy\stackchan_notify.py approval`。

### 2. 机器人不到一分钟就掉线
Stack-chan 默认固件为了省电，在没有持续交互时会自动进入休眠状态（屏幕变暗并断开 WiFi/WebSocket 连接）。
为了解决这个问题，在执行阶段我将会：
*   编写一个**心跳保活脚本 (Keep-Alive Script)**。
*   该脚本会在后台运行，每隔 30 秒向机器人发送一次无感知的状态查询指令（或者轻微的动作），从而“骗”过它的休眠计时器，让它永远保持唤醒和在线状态。

## 项目结构 (供导出至 GitHub)

*   `firmware/`: 包含预编译的固件 `merged-binary.bin` 以及烧录说明。
*   `gateway/`: 包含支持 Edge TTS 语音引擎的 StackChan-MCP 网关程序。
*   `scripts/`: 包含 `stackchan_notify.py` 核心控制脚本和 `keep_alive.py`。

## 快速开始

### 1. 固件烧录 (Firmware)

1.  将 Stack-chan 通过 USB 连接到电脑。
2.  进入 `firmware/` 目录。
3.  **⚠️ 重要：备份与烧录安全注意事项**
    全量烧录 `merged-binary.bin` 到 `0x0` 会**覆盖** WiFi 配置（NVS 分区）和人脸包/皮肤（Assets 分区）。为避免数据丢失，请务必执行以下安全烧录流程：
    *   **NVS 分区 (WiFi 配置)**：位于 `0x9000`，大小 16KB (`0x4000`)。
    *   **Assets 分区 (人脸包/皮肤)**：位于 `0x800000`，大小 8MB (`0x800000`)。

    **安全烧录流程（以 COM3 为例，请按实际修改 `--port`）：**
    *   **步骤 A (备份)**：
        ```bash
        python -m esptool --port COM3 read_flash 0x9000 0x4000 nvs_backup.bin
        python -m esptool --port COM3 read_flash 0x800000 0x800000 assets_backup.bin
        ```
    *   **步骤 B (烧录固件)**：
        ```bash
        python -m esptool --chip esp32s3 --port COM3 -b 460800 write_flash 0x0 merged-binary.bin
        ```
    *   **步骤 C (恢复备份)**：
        ```bash
        python -m esptool --port COM3 --baud 921600 write_flash 0x9000 nvs_backup.bin
        python -m esptool --port COM3 --baud 921600 write_flash 0x800000 assets_backup.bin
        ```

    *(注：如果仅是日常迭代更新应用层，请尽量只烧录 `xiaozhi.bin` 到 `0x20000`，这样不会影响 NVS 和 Assets：`esptool.py --chip esp32s3 --port COM3 -b 460800 write_flash 0x20000 build/xiaozhi.bin`)*


4.  烧录完成后，机器人会显示 WiFi 配置界面。连接机器人的热点，在网页中配置：
    *   **WiFi**: 你的局域网信息。
    *   **Server URL**: `ws://<你电脑的局域网IP>:8765`
    *   **Token**: `stackchan`

### 2. 控制端部署 (Gateway)

1.  确保电脑已安装 [uv](https://github.com/astral-sh/uv)。
2.  进入 `gateway/` 目录。
3.  安装依赖：
    ```bash
    uv sync
    ```
4.  配置环境：
    复制 `.env.example` 为 `.env`，确保包含以下内容：
    ```env
    STACKCHAN_TTS_ENGINE=edge
    MCP_HTTP_PORT=8767
    ```

### 3. 配置 Gemini CLI

为了让 Gemini CLI 能够自动触发机器人提醒，请将以下内容添加到你的 Gemini CLI 全局配置或项目配置中（例如 `GEMINI.md` 或 `MEMORY.md`）：

> **系统提示/指令补充：**
> 
> 在以下场景中，请自动通过控制 Stack-chan 机器人提供反馈：
> 1.  **准备询问用户 (ask_user)**: 在调用前先运行 `uv run python scripts/stackchan_notify.py approval`。
> 2.  **任务成功完成**: 在最后一步完成后运行 `uv run python scripts/stackchan_notify.py done`。
> 3.  **发生致命错误**: 任务中断时运行 `uv run python scripts/stackchan_notify.py error`。

## 解决机器人休眠掉线问题

Stack-chan 固件默认开启了节电休眠（通常是几分钟无交互即进入休眠断开连接）。为了保持长连接，可以通过调用设备的 `set_gateway_config` 工具来禁用休眠，或者在网关端添加一个定期发送心跳包（Ping/状态查询）的保活机制。本项目推荐使用心跳保活脚本。

## 核心脚本说明

使用 `scripts/stackchan_notify.py` 可以手动测试：

*   `python stackchan_notify.py approval` - 抬头 + 惊讶脸 + “有任务需要审批”
*   `python stackchan_notify.py done` - 点头 + 开心脸 + “任务完成”
*   `python stackchan_notify.py error` - 低头 + 伤心脸 + “代码出错了”

## 技术细节

*   **语音引擎**: 使用 Edge TTS (免费且无需本地服务器)。
*   **通信协议**: 基于 MCP (Model Context Protocol) 协议。
*   **编码依赖**: Windows 用户需确保 `gateway/stackchan_mcp/_libs/` 下有 `opus.dll`（本项目已内置）。
