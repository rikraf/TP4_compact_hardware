# FPGA Development Board Research for Timepix 4

## Requirements Summary

| Requirement | Specification |
|---|---|
| FPGA Family | Xilinx (AMD) |
| MGT inputs on FMC/FMC+ | 4–16, operating at **5.12 Gb/s** |
| Additional LVDS pairs | ≥10 on same connector |
| Power supply to FPGA | 5V–12V, ≥5W |
| Network | ≥10 Gb/s (10GbE, 40GbE, 100GbE, USB3, etc.) |
| Price | < $5,000 retail |

---

## Boards Under Evaluation

### 1. AMD Zynq UltraScale+ ZCU102 — $3,234

**FPGA:** XCZU9EG-2FFVB1156I (Zynq UltraScale+ MPSoC)

| Parameter | Value |
|---|---|
| FMC connectors | 2× FMC-HPC |
| MGT on FMC | **16× GTH @ up to 16.3 Gb/s** (total across both HPC connectors) |
| LVDS pairs on FMC | 64 user-defined differential I/Os |
| Networking | 4× SFP+ cages (10GbE via PL MAC/PHY) + 1× GbE |
| Power input | 12V |
| Price | ~$3,234 |

**Assessment vs. requirements:**
- ✅ MGT count: 16 GTH transceivers on the FMC connectors, well above the 4–16 minimum. 16.3 Gb/s max rate is comfortably above the 5.12 Gb/s requirement.
- ✅ LVDS: 64 user-defined differential pairs across the two FMC-HPC connectors (>>10 required).
- ✅ Networking: 4× SFP+ supporting 10GbE each; 40 Gb/s aggregate available.
- ✅ Power: 12V input, ample power delivery.
- ✅ Price: $3,234 — under the $5,000 cap.
- ⚠️ The FMC connectors are standard VITA 57.1 HPC, not FMC+ (VITA 57.4). If the TP4 FMC card uses FMC+ (high-pin-count plus), verify mechanical and signal compatibility.

**Notes:** The ZCU102 is AMD's flagship MPSoC evaluation board and is widely used in physics/detector readout projects. Strong community support, full Vivado/Vitis integration, and stable BSPs. The Zynq PS (quad-core ARM + FPGA fabric) is a significant advantage for embedded control. Pricing can vary by distributor; check Arrow, Avnet, Mouser.

---

### 2. ALINX AXKU042 — ~$1,168

**FPGA:** Xilinx Kintex UltraScale XCKU040

| Parameter | Value |
|---|---|
| FMC connectors | 2× FMC-LPC + **1× FMC-HPC** |
| MGT on FMC-HPC | **8× GTH @ up to 12.5 Gb/s** (BANK227/228, exposed on HPC connector) |
| MGT on FMC-LPC | 1× GTH per LPC connector (BANK226) |
| LVDS pairs on FMC-HPC | 58 pairs (BANK66/67/68) |
| LVDS pairs on FMC-LPC | 36 pairs per LPC connector |
| Networking | 2× SFP+ @ 10/12.5 Gbps each + 1× GbE |
| Power input | 12V single supply |
| Price | ~$1,168 |

**Assessment vs. requirements:**
- ✅ MGT count: 8 GTH on the HPC connector exceeds the 4-MGT minimum. 12.5 Gb/s max rate is well above 5.12 Gb/s.
- ✅ LVDS: 58 differential pairs on the HPC connector alone (>>10 required).
- ✅ Networking: 2× 10G SFP+ satisfies the ≥10 Gb/s requirement.
- ✅ Power: 12V single supply.
- ✅ Price: Substantially under budget at ~$1,168.
- ⚠️ **Only 8 MGT on the HPC connector** — if TP4 needs all 16 MGTs routed through a single FMC, this falls short. Using both LPC connectors adds 2 more GTH, for a total of 10, but LPC connectors carry fewer signals and may not carry the required MGT lanes to the right pin positions.
- ⚠️ This is a third-party (ALINX) board. Support is less comprehensive than AMD's official evaluation kits. Schematics and Verilog demos are provided, but integration into an existing TP4 firmware environment may require more effort.
- ⚠️ The XCKU040 is a pure FPGA (no ARM processor), unlike the Zynq-based boards. If TP4 firmware relies on a soft or hard processor, verify this is sufficient.

**AXKU062 variant:** The same board form factor is available with an XCKU060 (larger Kintex UltraScale device) at a higher price (~$1,500–$1,800). The connector arrangement and MGT count are identical; this only buys more LUTs/DSPs/BRAMs.

---

### 3. AMD Kria KR260 — ~$349

**FPGA/SOM:** Kria K26 SOM (custom XCK26, Zynq UltraScale+ MPSoC EV architecture)

| Parameter | Value |
|---|---|
| FMC connectors | **None** — uses proprietary 240-pin SOM connectors |
| MGT accessible | 4× GTH (via SFP+ and SOM connectors); formal FMC routing not present |
| LVDS pairs | Limited; accessible via SOM expansion header, not a standard FMC |
| Networking | 4× GbE + 1× SFP+ (10GbE) |
| Power input | 12V, 36W |
| Price | ~$349 |

**Assessment vs. requirements:**
- ❌ **No FMC connector.** The KR260 does not have an FMC or FMC+ connector. The TP4 requirement explicitly calls for MGTs and LVDS pairs on an FMC or FMC+ connector. The KR260 exposes interfaces only through its SOM connectors and on-board peripherals.
- ❌ MGT availability on a standard mezzanine connector is not supported without designing a custom carrier card.
- ✅ Price is very attractive at ~$349.
- ✅ Networking: 1× SFP+ at 10 GbE meets the networking requirement.

**Conclusion:** The KR260 is **not suitable as a drop-in solution** for TP4 in its current form. It would require a custom carrier card to expose FMC-compatible connectivity, which is a significant engineering effort and additional cost.

---

## Additional Board Worth Considering

### HiTech Global KU060 PCIe Board — $4,995

**FPGA:** Xilinx Kintex UltraScale XCKU060

| Parameter | Value |
|---|---|
| FMC connectors | **2× FMC-HPC** |
| MGT on FMC | **10× GTH per HPC connector (20 total)** |
| LVDS pairs on FMC | 160 single-ended I/Os per connector (80 LVDS pairs) |
| Networking | PCIe Gen3 ×8 (host interface); no onboard SFP+ |
| Power input | 12V/8A standalone adapter |
| Price | $4,995 |

**Assessment vs. requirements:**
- ✅ MGT: 20 GTH total across two HPC connectors — excellent for TP4 with up to 16 required.
- ✅ LVDS: 80+ differential pairs per HPC connector.
- ⚠️ Networking: The KU060 board from HiTech Global is primarily a PCIe compute card. There is no onboard SFP+ or direct 10GbE; network connectivity would need to be via the PCIe host or an FMC network module. This may not satisfy the TP4 standalone networking requirement.
- ⚠️ Price: At $4,995 it is just under the $5,000 limit, leaving no margin.
- ⚠️ Uses a pure FPGA (no ARM processor).

---

## Comparison Summary

| Board | FPGA | MGTs on FMC | LVDS on FMC | 10G+ Network | FMC Type | Price | Overall |
|---|---|---|---|---|---|---|---|
| **ZCU102** | Zynq US+ XCZU9EG | 16× GTH (16.3 Gb/s) | 64 pairs | 4× SFP+ (10GbE) | 2× HPC | $3,234 | ✅ Meets all requirements |
| **AXKU042** | Kintex US XCKU040 | 8× GTH (12.5 Gb/s) on HPC | 58 pairs | 2× SFP+ (10G) | 1 HPC + 2 LPC | $1,168 | ✅ Meets most; verify MGT count |
| **KR260** | Kria K26 (Zynq US+) | None (no FMC) | None (no FMC) | 1× SFP+ (10GbE) | No FMC | $349 | ❌ No FMC — not suitable |
| **HTG KU060** | Kintex US XCKU060 | 20× GTH (total) | 80+ pairs | PCIe only | 2× HPC | $4,995 | ⚠️ No native 10GbE |

---

## Recommendations

**Best overall fit: ZCU102 ($3,234)**
The ZCU102 satisfies all stated requirements with margin. Its 16 GTH transceivers on standard FMC-HPC connectors, 64 LVDS pairs, and 4× 10GbE SFP+ cages are exactly what TP4 needs. The integrated ARM processor in the Zynq MPSoC is a practical bonus for run control and data handling. It is an official AMD product with long-term availability, full documentation, and broad community use in physics detector applications.

**Best value if 8 MGTs is sufficient: AXKU042 ($1,168)**
At roughly one-third the price of the ZCU102, the AXKU042 is compelling if TP4 requires 4–8 MGTs (not the full 16). The HPC connector carries 8 GTH transceivers at up to 12.5 Gb/s, and the 2× 10G SFP+ satisfies networking. The main risks are the third-party support model and the lack of a hard processor. **Before committing, verify that the XCKU040 HPC pinout maps correctly to the TP4 FMC card's MGT requirements.**

**KR260 — only if custom carrier board is planned**
The Kria KR260 is not a plug-in solution for TP4 due to the absence of an FMC connector. It could serve as a starting point for a fully custom carrier board design (leveraging the SOM's low cost and Zynq processor), but that is a significant development investment beyond the scope of a "cheaper FPGA board" evaluation.

---

*Research compiled June 2026. Prices are indicative and subject to change by distributor.*
