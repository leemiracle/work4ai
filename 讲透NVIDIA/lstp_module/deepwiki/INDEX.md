# DeepWiki 索引 — NVIDIA/lstp_module

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 24 页 · 全文 154082 字符

- [1 LSTP Driver Overview](1-lstp-driver-overview.md)
  - [1.1 Project Background and Protocol Specification](1.1-project-background-and-protocol-specification.md)
  - [1.2 Getting Started: Build, Install, and Load](1.2-getting-started-build-install-and-load.md)
  - [1.3 Security and Licensing](1.3-security-and-licensing.md)
- [2 Core Driver Architecture](2-core-driver-architecture.md)
  - [2.1 USB Transport and Channel Multiplexing](2.1-usb-transport-and-channel-multiplexing.md)
  - [2.2 Wire Protocol: Packet Format and Status Codes](2.2-wire-protocol-packet-format-and-status-codes.md)
  - [2.3 Subsystem Registration Framework](2.3-subsystem-registration-framework.md)
  - [2.4 Request/Response API and Synchronization](2.4-request-response-api-and-synchronization.md)
  - [2.5 Sysfs Hierarchy and Firmware Node Integration](2.5-sysfs-hierarchy-and-firmware-node-integration.md)
- [3 Transport Subsystems](3-transport-subsystems.md)
  - [3.1 SPI Subsystem (lstp-spi.c)](3.1-spi-subsystem-lstp-spi.c.md)
  - [3.2 GPIO Subsystem (lstp-gpio.c)](3.2-gpio-subsystem-lstp-gpio.c.md)
  - [3.3 I2C Subsystem (lstp-i2c.c)](3.3-i2c-subsystem-lstp-i2c.c.md)
  - [3.4 UART Subsystem (lstp-uart.c)](3.4-uart-subsystem-lstp-uart.c.md)
  - [3.5 IPMI Subsystem (lstp-ipmi.c and lstp-ipmi-postcodes.h)](3.5-ipmi-subsystem-lstp-ipmi.c-and-lstp-ipmi-postcodes.h.md)
  - [3.6 MMIO Subsystem (lstp-mmio.c)](3.6-mmio-subsystem-lstp-mmio.c.md)
- [4 Device Tree Bindings](4-device-tree-bindings.md)
  - [4.1 Top-Level LSTP USB Device Binding (nvidia,lstp.yaml)](4.1-top-level-lstp-usb-device-binding-nvidia-lstp.yaml.md)
  - [4.2 Per-Peripheral Channel Bindings](4.2-per-peripheral-channel-bindings.md)
- [5 Development and Tooling](5-development-and-tooling.md)
  - [5.1 Code Style and Formatting](5.1-code-style-and-formatting.md)
  - [5.2 Coding Conventions and Compatibility Guidelines](5.2-coding-conventions-and-compatibility-guidelines.md)
- [6 Glossary](6-glossary.md)
