# XMeye Integration for Home Assistant

This custom integration allows you to connect DVRs and IP Cameras using the XMeye protocol (common in Chinese devices using the DVRIP protocol).

## Features

- Auto-detection of available camera channels
- Still image capture
- Works with low-cost DVRs (e.g., H.264, H.265, HiSilicon based)

## Installation

1. Install via HACS:
   - Add this repo as a custom repository (see below).
   - Search for **XMeye** in HACS Integrations and install.

2. Restart Home Assistant.

3. Go to **Settings > Devices & Services > Add Integration**, search for **XMeye**, and follow the instructions.

## Adding as Custom Repository in HACS

1. Open HACS > Integrations
2. Click on the three dots (⋮) > Custom Repositories
3. Enter:
   - URL: `https://github.com/AriasCaldeira/xmeye-homeassistant`
   - Category: Integration
4. Click **Add**.

## Credits

- Built using [dvrip](https://github.com/quatanium/python-dvr) protocol client
- Integration maintained by @AriasCaldeira
