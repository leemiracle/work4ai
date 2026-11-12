# Rivermax Input API Drain Detached Flow Demo Application

## Description

This application demonstrates how to drain data from a detached flow.

Key features include:
 * Attaching and detaching multiple flows to the same receive stream.
 * Using flow\_id to distinguish between different flows.
 * Processing packets from a flow that has already detached but still has
   remaining data in the receive buffer.
