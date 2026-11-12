<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

This is a small example federation with one app that greets its users.

The configuration files of the federation are in `examplefed/configs`.

The packages `examplefed.fed.api`, `examplefed.fed.runtime`, and `examplefed.fed.site` are
generated from the `examplefed/configs/federation.dfm.yaml`. You should not
change any contents of the `fed/` subfolder (python package)
because the folders will be deleted
and re-generated the next time. But you can freely work in any other packages
and folders in `examplefed`.

The `examplefed` federation comes with its own custom adapters.
The first custom adapter is `examplefed.lib.customer_service.GreetMe` that sends
a heartfelt greeting back to the user.
The second custom adapter is `examplefed.lib.customer_service.GreetMeReception`
which sends a slightly more formal `GreetMe` message, 
configured to be used by the `reception` site
of the `examplefed` federation.
Note: The custom adapters can be placed in any python package (except
for the aforementioned generated packages), but using `lib` is a good practice.
There are adapter libraries written and maintained by the `dfm` team (for example, `nv-dfm-lib-weather`)
but developers using federation can write their own just as well.

The `examplefed` comes with one app that uses the federation.
This app is called the `concierge` and is located in `examplefed.apps.concierge`.
Note: app code can be placed in any python package (except
for the aforementioned generated packages), but using `app` is a good practice.
It's a simple CLI tool that submits a pipeline to the dfm to let
it compute a greeting for the user.
