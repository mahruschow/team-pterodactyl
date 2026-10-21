# GPS integration evidence

Current board after user-authorized GPS geometry acceptance and targeted routing. See [GPS_CARRIER_INTEGRATION.md](../../../GPS_CARRIER_INTEGRATION.md).

- `drc.json`: all severities, parity and zone refill; zero enabled violations, zero unconnected, zero parity issues. Ignored categories are retained in the report.
- `erc.json`: zero schematic ERC violations.
- `layout-check.json`: live pad/hole/net, routing, spacing, I2C and inner-plane checks.
- `preservation-check.json`: exact parsed equality for all pre-existing footprint/track/via objects against the clean e2664ad working baseline; unchanged project bytes and independently checked 32 nets / 35 intentional no-connects.
- `board.svg`: current assembly/copper preview.

These files do not establish physical module fit or fabrication approval.
