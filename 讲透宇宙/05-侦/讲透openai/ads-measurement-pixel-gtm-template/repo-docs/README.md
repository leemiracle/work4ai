# OpenAI Ads Measurement Pixel GTM Template

This repository contains the Google Tag Manager web tag template for the
OpenAI Ads Measurement Pixel. It lets advertisers install and configure the
pixel without writing custom JavaScript.

## Install

To import the template manually:

1. In Google Tag Manager, open **Templates**.
2. Under **Tag Templates**, select **New**.
3. Open the overflow menu and select **Import**.
4. Choose `template.tpl` from this repository.
5. Review the requested permissions and save the template.

Once the template is available in the GTM Community Template Gallery, install
it from **Templates > Tag Templates > Search Gallery** instead.

## Configure

Create an OpenAI Ads Measurement Pixel tag for each event you want to measure:

1. Enter your OpenAI Ads Measurement Pixel ID.
2. Leave **Send a measurement event when this tag fires** enabled.
3. Select the event and provide any applicable event fields.
4. Choose the GTM trigger for that event.
5. Save the tag and publish the container.

Use the same Pixel ID for every OpenAI Ads Measurement Pixel tag in the
container.

You may also create an optional base tag that only initializes the pixel:

- Disable **Send a measurement event when this tag fires**.
- Use an Initialization or All Pages trigger.

Event tags initialize the pixel themselves, so the base tag is not required.

The per-event opt-out field can use a GTM Data Layer Variable that resolves to
`true`, `false`, or an empty value.

## Test

Use GTM Preview before publishing:

1. Confirm the expected OpenAI Ads Measurement Pixel tag fires.
2. Confirm the configured event is sent.

## Documentation

See the [OpenAI Ads measurement pixel documentation](https://developers.openai.com/ads/measurement-pixel)
for event definitions, field requirements, data layer examples, and additional
setup guidance.

## Security

To report a security issue, follow [SECURITY.md](SECURITY.md).

## License

Copyright 2026 OpenAI

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
