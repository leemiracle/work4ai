===== packages/llm/README.md (50 lines) =====

===== packages/llm/deepseek-llm-api-extensions/README.md (61 lines) =====

===== packages/llm/deepseek-llm-api-extensions/package.json (42 lines) =====

===== packages/llm/deepseek-llm-api-extensions/src/index.ts (144 lines) =====
  import @deepseek-ai/cordis -> (external)
  import ./types.ts -> packages/llm/deepseek-llm-api-extensions/src/types.ts
  signals: extends Service, ctx.effect
  class DeepSeekLlmApiExtensionRegistry [66-142] extends Service
  fn freezeJson [32-38] (function)
  fn acceptAll [41-48] (function)
  fn abortable [51-63] (function)

===== packages/llm/deepseek-llm-api-extensions/src/types.ts (59 lines) =====

===== packages/llm/llm/README.md (199 lines) =====

===== packages/llm/llm/package.json (77 lines) =====

===== packages/llm/llm/src/adapter-failure.ts (107 lines) =====
  import ./error.ts -> packages/llm/llm/src/error.ts
  import ./types.ts -> packages/llm/llm/src/types.ts
  fn normalizeLlmFailure [16-28] (function, exported)
  fn thrownMessage [31-38] (function)
  fn ownErrorCode [41-48] (function)
  fn ownFailureSnapshot [51-60] (function)
  fn failureSnapshot [63-91] (function)
  fn errorMessage [94-102] (function)
  fn harnessErrorCode [105-107] (function)

===== packages/llm/llm/src/assembler.ts (208 lines) =====
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  import ./message.ts -> packages/llm/llm/src/message.ts
  import ./types.ts -> packages/llm/llm/src/types.ts
  class BlockAssembler [38-208]

===== packages/llm/llm/src/assistant-stream.ts (534 lines) =====
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./assembler.ts -> packages/llm/llm/src/assembler.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  import ./types.ts -> packages/llm/llm/src/types.ts
  class AssistantStreamAccumulator [100-194]
  fn safeTime [76-79] (function)
  fn safeIndex [81-86] (function)
  fn snapshotChunk [88-92] (function)
  fn safeGap [94-97] (function)
  fn expandAssistantStream [202-232] (function, exported)
  fn hasNonWhitespace [234-236] (function)
  fn blockIsVisible [238-242] (function)
  fn isTokenDelta [250-260] (function, exported)
  fn isVisibleChunk [270-282] (function, exported)
  fn chunkHasVisibleText [290-293] (function, exported)
  fn firstRunMemberTime [295-303] (function)
  fn runFirstTokenTime [312-315] (function, exported)
  fn runFirstVisibleTime [323-325] (function, exported)
  fn assistantStreamFirstTokenTime [333-341] (function, exported)
  fn assistantStreamHasVisibleContent [349-353] (function, exported)
  fn assistantStreamHasVisibleText [361-365] (function, exported)
  fn lastAssistantStreamChunk [373-382] (function, exported)
  fn assistantStreamChunks [390-399] (function, exported)
  fn joinAssistantStreamText [406-413] (function, exported)
  fn assembleAssistantStream [425-454] (function, exported)
  fn validateRecord [456-505] (function)
  fn validateRun [507-521] (function)
  fn stringArray [523-528] (function)
  fn exactKeys [530-534] (function)

===== packages/llm/llm/src/attribution.ts (68 lines) =====
  import node:module -> (external)
  fn userAgent [53-55] (function, exported)
  fn attributionHeaders [64-68] (function, exported)

===== packages/llm/llm/src/brand.ts (76 lines) =====
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  fn MessageId [23-25] (function, exported)
  fn ToolCallId [38-40] (function, exported)
  fn ProviderRequestId [50-52] (function, exported)
  fn LlmAttemptId [62-64] (function, exported)
  fn ReasoningEffortId [74-76] (function, exported)

===== packages/llm/llm/src/call-config.ts (96 lines) =====
  import ./types.ts -> packages/llm/llm/src/types.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  fn callConfigEquals [67-77] (function, exported)
  fn markAgentLoopRequest [84-87] (function, exported)
  fn isAgentLoopRequest [94-96] (function, exported)

===== packages/llm/llm/src/content.ts (510 lines) =====
  import ./types.ts -> packages/llm/llm/src/types.ts
  import ./message.ts -> packages/llm/llm/src/message.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  fn resolveImageAttachmentAccess [35-44] (function, exported)
  fn quoted [46-48] (function)
  fn imageIdentity [50-54] (function)
  fn extension [56-64] (function)
  fn normalizedAccessText [66-70] (function)
  fn textOnlyImageText [77-80] (function, exported)
  fn requestImageHandleText [92-101] (function, exported)
  fn offloadedImageText [109-118] (function, exported)
  fn contentHasImage [127-129] (function, exported)
  fn contentHasFile [137-142] (function, exported)
  fn fileHandleText [152-159] (function, exported)
  fn replaceFilesWithHandles [162-176] (function)
  fn projectFilesToText [186-209] (function, exported)
  fn projectFilesToText [196-209] (function, exported)
  fn projectFilesToText [200-209] (function, exported)
  fn base64Length [212-214] (function)
  fn visitImageBlocks [221-225] (function)
  fn replaceOffloadedImages [228-242] (function)
  fn projectOffloadedImages [252-274] (function, exported)
  fn projectOffloadedImages [262-274] (function, exported)
  fn projectOffloadedImages [266-274] (function, exported)
  fn offloadedImagePrefixCount [285-307] (function)
  fn requiredImageOffload [319-333] (function, exported)
  fn replaceImagesForTextModel [336-347] (function)
  fn projectImagesForTextModel [354-367] (function, exported)
  fn projectImagesForTextModel [360-367] (function, exported)
  fn projectImagesForTextModel [361-367] (function, exported)
  fn withoutDeveloperMessages [377-380] (function)
  fn toolDeclarations [382-394] (function)
  fn rebaseAdditionOnlyHistory [397-423] (function)
  fn projectToolUpdates [439-510] (function, exported)

===== packages/llm/llm/src/error.ts (175 lines) =====
  class HarnessError [13-22] extends Error
  fn isContextWindowExceededError [83-89] (function, exported)
  fn isQuotaExceededError [97-103] (function, exported)
  fn errorChain [117-157] (function, exported)
  fn isHarnessError [164-166] (function, exported)

===== packages/llm/llm/src/index.ts (1222 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-typert-protocol -> packages/typert/protocol/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./types.ts -> packages/llm/llm/src/types.ts
  import ./message.ts -> packages/llm/llm/src/message.ts
  import ./retry-policy.ts -> packages/llm/llm/src/retry-policy.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  import ./call-config.ts -> packages/llm/llm/src/call-config.ts
  import ./error.ts -> packages/llm/llm/src/error.ts
  import ./adapter-failure.ts -> packages/llm/llm/src/adapter-failure.ts
  import ./api-key.ts -> packages/llm/llm/src/api-key.ts
  import ./content.ts -> packages/llm/llm/src/content.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import ./attribution.ts -> packages/llm/llm/src/attribution.ts
  import ./assistant-stream.ts -> packages/llm/llm/src/assistant-stream.ts
  import ./assembler.ts -> packages/llm/llm/src/assembler.ts
  signals: ctx.effect
  class LlmError [96-131] extends HarnessError
  class LlmAdapter [208-303]
  class LlmRuntime [354-1185] extends TypertRemoteService
  fn assertUsableApiKey [151-166] (function, exported)
  fn adapterFailureChunk [1188-1196] (function)
  fn detachDirectoryEntry [1199-1207] (function)

===== packages/llm/llm/src/message.ts (307 lines) =====
  import @deepseek-ai/dsh-util-crypto -> packages/util/crypto/src/index.ts
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  import ./types.ts -> packages/llm/llm/src/types.ts
  fn boundContextSummary [129-133] (function, exported)
  fn freezeMessage [212-214] (function, exported)
  fn createMessage [221-228] (function, exported)
  fn createDeveloperMessage [235-239] (function, exported)
  fn createUserMessage [246-253] (function, exported)
  fn createAssistantMessage [260-271] (function, exported)
  fn createSystemMessage [279-285] (function, exported)
  fn createToolResultMessage [299-307] (function, exported)

===== packages/llm/llm/src/types.ts (606 lines) =====
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-package-manifest -> packages/util/package-manifest/src/index.ts
  import ./brand.ts -> packages/llm/llm/src/brand.ts
  import ./message.ts -> packages/llm/llm/src/message.ts

===== packages/llm/llm/tsconfig.json (42 lines) =====

===== packages/llm/llm-deepseek/README.md (221 lines) =====

===== packages/llm/llm-deepseek/package.json (88 lines) =====

===== packages/llm/llm-deepseek/src/adapter.ts (182 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-deepseek-llm-api-extensions -> packages/llm/deepseek-llm-api-extensions/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import ./model-info.ts -> packages/llm/llm-deepseek/src/model-info.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  import ./file-store.ts -> packages/llm/llm-deepseek/src/file-store.ts
  import ./messages-api.ts -> packages/llm/llm-deepseek/src/messages-api.ts
  import ./request-files.ts -> packages/llm/llm-deepseek/src/request-files.ts
  import ./request-extensions.ts -> packages/llm/llm-deepseek/src/request-extensions.ts
  import ./images.ts -> packages/llm/llm-deepseek/src/images.ts
  import ./serialize.ts -> packages/llm/llm-deepseek/src/serialize.ts
  import ./sse.ts -> packages/llm/llm-deepseek/src/sse.ts
  import ./translate.ts -> packages/llm/llm-deepseek/src/translate.ts
  import ./transport.ts -> packages/llm/llm-deepseek/src/transport.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import ./request-pricing.ts -> packages/llm/llm-deepseek/src/request-pricing.ts
  class DeepSeekAdapter [22-182] extends LlmAdapter

===== packages/llm/llm-deepseek/src/config.ts (340 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/cosmokit -> (external)
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  import ./models.ts -> packages/llm/llm-deepseek/src/models.ts
  import ./defaults.ts -> packages/llm/llm-deepseek/src/defaults.ts
  import ./request-pricing.ts -> packages/llm/llm-deepseek/src/request-pricing.ts
  fn plainOptions [65-67] (function, exported)
  fn isBuiltInCatalog [130-132] (function, exported)
  fn resolveModels [135-210] (function)
  fn resolveAdapterOptions [225-340] (function, exported)

===== packages/llm/llm-deepseek/src/credential.ts (58 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-credentials -> packages/credentials/credentials/src/index.ts
  import @deepseek-ai/dsh-deepseek-account -> packages/credentials/deepseek-account/src/index.ts
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  fn resolveDeepSeekApiKey [15-23] (function, exported)
  fn deepSeekApiKeyConfigured [31-36] (function, exported)
  fn resolveDeepSeekAccountToken [44-46] (function, exported)
  fn rejectDeepSeekAccountToken [55-58] (function, exported)

===== packages/llm/llm-deepseek/src/defaults.ts (24 lines) =====

===== packages/llm/llm-deepseek/src/file-store.ts (336 lines) =====
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./files-api.ts -> packages/llm/llm-deepseek/src/files-api.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  import ./messages-api.ts -> packages/llm/llm-deepseek/src/messages-api.ts
  import ./upload-index.ts -> packages/llm/llm-deepseek/src/upload-index.ts
  class DeepSeekFileStore [121-336]
  fn fileScope [49-54] (function)
  fn abortReason [56-61] (function)
  fn uploadFailure [63-67] (function)
  fn waitForUpload [69-103] (function)
  fn extension [105-112] (function)
  fn filename [114-118] (function)

===== packages/llm/llm-deepseek/src/files-api.ts (262 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  import ./messages-api.ts -> packages/llm/llm-deepseek/src/messages-api.ts
  class DeepSeekFilesError [39-59] extends LlmError
  class DeepSeekFilesClient [131-262]
  fn isFilesQuotaError [66-69] (function, exported)
  fn invalidResponse [78-80] (function)
  fn responseJson [83-93] (function)
  fn parseFileObject [95-114] (function)
  fn providerErrorDetail [116-128] (function)

===== packages/llm/llm-deepseek/src/host.ts (91 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-settings -> packages/settings/settings/src/index.ts
  import @deepseek-ai/cordis-plugin-loader -> (external)
  import @deepseek-ai/dsh-fs -> packages/fs/fs/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-anonymous-user-id -> packages/identity/anonymous-user-id/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./adapter.ts -> packages/llm/llm-deepseek/src/adapter.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  import ./listing-cache.ts -> packages/llm/llm-deepseek/src/listing-cache.ts
  signals: ctx.effect, ctx.on
  fn createModelListingCache [21-36] (function, exported)
  fn registerDeepSeekProvider [44-91] (function, exported)

===== packages/llm/llm-deepseek/src/image-tokens.ts (157 lines) =====
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  fn intDiv [27-27] (arrow/const)
  fn ceilDiv [28-28] (arrow/const)
  fn gridTokens [39-41] (function)
  fn gridCells [44-46] (function)
  fn solveResizeRatio [49-75] (function)
  fn safeResize [78-96] (function)
  fn resizeOnce [99-111] (function)
  fn sameResize [113-119] (function)
  fn deepSeekRequestImageDimensions [132-138] (function, exported)
  fn deepSeekImageTokens [147-157] (function, exported)

===== packages/llm/llm-deepseek/src/images.ts (111 lines) =====
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  import ./request-pricing.ts -> packages/llm/llm-deepseek/src/request-pricing.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  import ./request-files.ts -> packages/llm/llm-deepseek/src/request-files.ts
  fn bounds [13-21] (function)
  fn imageRefs [23-27] (function)
  fn prepareImages [38-61] (function, exported)
  fn inlineImages [69-75] (function, exported)
  fn assertImagesFit [78-91] (function)
  fn prepareFileIds [99-111] (function, exported)

===== packages/llm/llm-deepseek/src/index.ts (50 lines) =====
  import ./credential.ts -> packages/llm/llm-deepseek/src/credential.ts
  import ./config.ts -> packages/llm/llm-deepseek/src/config.ts
  import ./defaults.ts -> packages/llm/llm-deepseek/src/defaults.ts
  import ./adapter.ts -> packages/llm/llm-deepseek/src/adapter.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  import ./request-pricing.ts -> packages/llm/llm-deepseek/src/request-pricing.ts
  import ./image-tokens.ts -> packages/llm/llm-deepseek/src/image-tokens.ts
  import ./file-store.ts -> packages/llm/llm-deepseek/src/file-store.ts
  import ./files-api.ts -> packages/llm/llm-deepseek/src/files-api.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  import ./upload-index.ts -> packages/llm/llm-deepseek/src/upload-index.ts
  import ./model-info.ts -> packages/llm/llm-deepseek/src/model-info.ts
  import ./host.ts -> packages/llm/llm-deepseek/src/host.ts
  import ./listing.ts -> packages/llm/llm-deepseek/src/listing.ts
  import ./listing-config.ts -> packages/llm/llm-deepseek/src/listing-config.ts
  import ./listing-cache.ts -> packages/llm/llm-deepseek/src/listing-cache.ts
  import ./listed-catalog.ts -> packages/llm/llm-deepseek/src/listed-catalog.ts

===== packages/llm/llm-deepseek/src/listed-catalog.ts (186 lines) =====
  import semver -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./config.ts -> packages/llm/llm-deepseek/src/config.ts
  import ./listing.ts -> packages/llm/llm-deepseek/src/listing.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  fn layered [49-56] (function)
  fn listed [59-74] (function)
  fn gateOf [76-94] (function)
  fn resolveListedCatalog [103-164] (function, exported)
  fn refuseListedModel [172-186] (function, exported)

===== packages/llm/llm-deepseek/src/listing-cache.ts (202 lines) =====
  import node:crypto -> (external)
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./listing-config.ts -> packages/llm/llm-deepseek/src/listing-config.ts
  import ./listing.ts -> packages/llm/llm-deepseek/src/listing.ts
  class ModelListingCache [49-202]
  fn abandonable [36-46] (function)

===== packages/llm/llm-deepseek/src/listing-config.ts (64 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  fn resolveListingTiming [55-64] (function, exported)

===== packages/llm/llm-deepseek/src/listing.ts (269 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  fn modelListingURL [24-26] (function, exported)
  fn fieldsOf [85-87] (function)
  fn knownModalities [90-95] (function)
  fn capacity [98-101] (function)
  fn requirementOf [103-115] (function)
  fn badgeText [118-124] (function)
  fn localizedBadgeText [127-140] (function)
  fn OWN_METADATA [143-148] (arrow/const)
  fn optionalFields [146-148] (function)
  fn badgeOf [150-170] (function)
  fn capabilitiesOf [172-199] (function)
  fn parseModelListing [207-229] (function, exported)
  fn requestModelListing [241-269] (function, exported)

===== packages/llm/llm-deepseek/src/messages-api.ts (17 lines) =====
  fn messagesApiRoot [14-17] (function, exported)

===== packages/llm/llm-deepseek/src/model-info.ts (102 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  fn catalogModelInfo [46-55] (function, exported)
  fn modelInfo [63-102] (function, exported)

===== packages/llm/llm-deepseek/src/models.ts (23 lines) =====
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts

===== packages/llm/llm-deepseek/src/replay.ts (64 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  fn object [17-22] (function, exported)
  fn replayState [29-31] (function, exported)
  fn readReplay [39-46] (function, exported)
  fn validateReplay [48-64] (function)

===== packages/llm/llm-deepseek/src/request-extensions.ts (59 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-deepseek-llm-api-extensions -> packages/llm/deepseek-llm-api-extensions/src/index.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  fn prepareRequestExtensions [21-59] (function, exported)

===== packages/llm/llm-deepseek/src/request-files.ts (158 lines) =====
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import ./file-store.ts -> packages/llm/llm-deepseek/src/file-store.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  class FileResolutionFailure [15-20] extends Error
  class RequestFiles [94-158]
  fn providerRejectedNormalizedImage [22-26] (function)
  fn providerRejectedFileId [34-39] (function)
  fn detailNamesFileId [41-51] (function)
  fn staleMappings [53-60] (function)
  fn normalizedImageFacts [62-70] (function)
  fn normalizedImageDiagnostic [72-90] (function)

===== packages/llm/llm-deepseek/src/request-pricing.ts (111 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import ./image-tokens.ts -> packages/llm/llm-deepseek/src/image-tokens.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  fn resolveRequestImageMaxBytes [39-41] (function, exported)
  fn resolveRequestImageTarget [53-65] (function, exported)
  fn textOnlyPrice [72-74] (function)
  fn deepSeekImageRequestPricing [90-111] (function, exported)

===== packages/llm/llm-deepseek/src/serialize.ts (169 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import ./types.ts -> packages/llm/llm-deepseek/src/types.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  import ./replay.ts -> packages/llm/llm-deepseek/src/replay.ts
  import ./wire-types.ts -> packages/llm/llm-deepseek/src/wire-types.ts
  fn unsupported [11-13] (function)
  fn toolInput [16-24] (function)
  fn assistant [26-39] (function)
  fn serialize [57-169] (function, exported)

===== packages/llm/llm-deepseek/src/sse.ts (28 lines) =====
  import eventsource-parser/stream -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./replay.ts -> packages/llm/llm-deepseek/src/replay.ts
  import ./transport.ts -> packages/llm/llm-deepseek/src/transport.ts
  fn parseSse [13-28] (function, exported)

===== packages/llm/llm-deepseek/src/translate.ts (166 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./replay.ts -> packages/llm/llm-deepseek/src/replay.ts
  fn string [20-23] (function, exported)
  fn malformed [25-27] (function)
  fn indexOf [29-32] (function)
  fn updateUsage [34-43] (function)
  fn startBlock [45-63] (function)
  fn deltaChunk [65-88] (function)
  fn stopReason [90-97] (function)
  fn translate [104-166] (function, exported)

===== packages/llm/llm-deepseek/src/transport.ts (44 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  fn providerErrorDetail [9-14] (function, exported)
  fn providerError [22-44] (function, exported)

===== packages/llm/llm-deepseek/src/types.ts (133 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-anonymous-user-id -> packages/identity/anonymous-user-id/src/index.ts
  import @deepseek-ai/dsh-deepseek-llm-api-extensions -> packages/llm/deepseek-llm-api-extensions/src/index.ts
  import ./file-store.ts -> packages/llm/llm-deepseek/src/file-store.ts

===== packages/llm/llm-deepseek/src/upload-index.ts (224 lines) =====
  import node:crypto -> (external)
  import node:fs/promises -> (external)
  import node:path -> (external)
  import @deepseek-ai/dsh-atomic-write -> packages/util/atomic-write/src/index.ts
  import @deepseek-ai/dsh-home-paths -> packages/util/home-paths/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import ./file-id.ts -> packages/llm/llm-deepseek/src/file-id.ts
  class InvalidUploadIndexError [31-37] extends Error
  class DeepSeekUploadIndex [112-224]
  fn deepSeekFileScope [45-52] (function, exported)
  fn absent [54-56] (function)
  fn parseRecord [58-81] (function)
  fn parseIndex [83-105] (function)
  fn reusable [107-109] (function)

===== packages/llm/llm-deepseek/src/wire-types.ts (41 lines) =====

===== packages/llm/llm-deepseek/tsconfig.json (62 lines) =====

===== packages/llm/llm-deepseek-account/README.md (106 lines) =====

===== packages/llm/llm-deepseek-account/package.json (61 lines) =====

===== packages/llm/llm-deepseek-account/src/config.ts (97 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/cosmokit -> (external)
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-llm-deepseek -> packages/llm/llm-deepseek/src/index.ts
  fn plainAccountOptions [54-56] (function, exported)
  fn resolveOverride [59-75] (function)
  fn resolveAccountOptions [84-97] (function, exported)

===== packages/llm/llm-deepseek-account/src/index.ts (99 lines) =====
  import @deepseek-ai/cordis-plugin-loader -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-deepseek-account -> packages/credentials/deepseek-account/src/index.ts
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-llm-deepseek -> packages/llm/llm-deepseek/src/index.ts
  import ./config.ts -> packages/llm/llm-deepseek-account/src/config.ts
  fn apply [29-99] (function, exported)

===== packages/llm/llm-deepseek-account/tsconfig.json (36 lines) =====

===== packages/llm/llm-deepseek-api-key/README.md (97 lines) =====

===== packages/llm/llm-deepseek-api-key/package.json (55 lines) =====

===== packages/llm/llm-deepseek-api-key/src/config.ts (61 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-credentials -> packages/credentials/credentials/src/index.ts
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-llm-deepseek -> packages/llm/llm-deepseek/src/index.ts
  fn plainOptions [43-45] (function, exported)
  fn resolveAdapterOptions [51-61] (function, exported)

===== packages/llm/llm-deepseek-api-key/src/index.ts (124 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/cordis-plugin-loader -> (external)
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-llm-deepseek -> packages/llm/llm-deepseek/src/index.ts
  import ./config.ts -> packages/llm/llm-deepseek-api-key/src/config.ts
  signals: ctx.on
  fn apply [34-124] (function, exported)

===== packages/llm/llm-deepseek-api-key/tsconfig.json (33 lines) =====

===== packages/llm/llm-pi-ai/README.md (286 lines) =====

===== packages/llm/llm-pi-ai/package.json (72 lines) =====

===== packages/llm/llm-pi-ai/scripts/gen-provider-data.ts (160 lines) =====
  import node:child_process -> (external)
  import node:fs -> (external)
  import node:path -> (external)
  import node:url -> (external)
  import typescript -> (external)
  import @earendil-works/pi-ai -> (external)
  import @earendil-works/pi-ai/providers/all -> (external)
  import @earendil-works/pi-ai/compat -> (external)
  fn quote [19-19] (arrow/const)
  fn merge [30-35] (function)
  fn resolverEnv [42-85] (function, exported)
  fn generateProviderData [92-120] (function, exported)
  fn syncProviderData [127-155] (function, exported)

===== packages/llm/llm-pi-ai/src/adapter.ts (500 lines) =====
  import @earendil-works/pi-ai -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import ./config.ts -> packages/llm/llm-pi-ai/src/config.ts
  import ./context.ts -> packages/llm/llm-pi-ai/src/context.ts
  import ./models.ts -> packages/llm/llm-pi-ai/src/models.ts
  import ./stream.ts -> packages/llm/llm-pi-ai/src/stream.ts
  import ./types.ts -> packages/llm/llm-pi-ai/src/types.ts
  class PiAiAdapter [273-500] extends LlmAdapter
  fn profileOptions [140-157] (function)
  fn describableReasoningLevel [172-180] (function)
  fn resolveReasoningLevel [183-194] (function)
  fn reasoningInfo [212-227] (function)
  fn requestHeaderDiagnostic [230-237] (function)
  fn requestHeaders [240-266] (function)

===== packages/llm/llm-pi-ai/src/catalog.ts (987 lines) =====
  import @earendil-works/pi-ai/providers/all -> (external)
  import @earendil-works/pi-ai -> (external)
  class PiAiCatalogError [674-679] extends Error
  fn declaredInput [65-67] (function)
  fn servesChat [176-179] (function)
  fn catalogProviders [187-190] (function)
  fn catalogProvider [199-201] (function, exported)
  fn catalogProviderIds [208-210] (function, exported)
  fn catalogModels [217-221] (function, exported)
  fn compatGate [355-357] (function)
  fn configuredCompatEntries [514-520] (function)
  fn compatProtocols [528-530] (function)
  fn offeredCompatFields [538-540] (function)
  fn allOfferedCompatFields [549-555] (function)
  fn assertOfferedCompatFields [567-601] (function)
  fn invalid [677-679] (function)
  fn sharedCatalogApi [689-693] (function)
  fn resolveModelReasoning [720-774] (function)
  fn resolveModelCompat [797-828] (function)
  fn resolveRouteModels [858-987] (function, exported)

===== packages/llm/llm-pi-ai/src/config.ts (551 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @earendil-works/pi-ai -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-credentials -> packages/credentials/credentials/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./catalog.ts -> packages/llm/llm-pi-ai/src/catalog.ts
  import ./provider.ts -> packages/llm/llm-pi-ai/src/provider.ts
  fn assertServiceable [395-399] (function, exported)
  fn rejectRemovedFields [402-417] (function)
  fn assertValidHeaders [420-431] (function)
  fn resolveProfiles [441-551] (function, exported)

===== packages/llm/llm-pi-ai/src/context.ts (401 lines) =====
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-attachment -> packages/attachment/attachment/src/index.ts
  import @earendil-works/pi-ai -> (external)
  import ./replay.ts -> packages/llm/llm-pi-ai/src/replay.ts
  import ./config.ts -> packages/llm/llm-pi-ai/src/config.ts
  fn flattenText [23-28] (function)
  fn toolResultOf [32-47] (function)
  fn assertSupportedHistory [50-65] (function)
  fn userContent [67-98] (function)
  fn collectImageRefs [100-109] (function)
  fn prepareRequestImages [111-128] (function)
  fn piTool [131-133] (function)
  fn toolsOf [135-137] (function)
  fn splitSystemPrompt [148-158] (function)
  fn piContext [161-168] (function)
  fn appendDeveloper [171-201] (function)
  fn appendAssistant [203-214] (function)
  fn appendSharedHistory [217-246] (function)
  fn textOnlyContext [248-269] (function)
  fn requestImageTarget [301-303] (function, exported)
  fn toPiContext [315-350] (function, exported)
  fn toPiContext [335-350] (function, exported)
  fn toPiContext [341-350] (function, exported)
  fn toPiContextWithImages [352-401] (function)

===== packages/llm/llm-pi-ai/src/discovery.ts (363 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./catalog.ts -> packages/llm/llm-pi-ai/src/catalog.ts
  fn capacity [91-96] (function)
  fn label [99-104] (function)
  fn listingUrl [117-122] (function)
  fn readBounded [130-165] (function)
  fn readListing [181-230] (function)
  fn usableProbeKey [240-249] (function)
  fn discoverModels [269-363] (function, exported)

===== packages/llm/llm-pi-ai/src/index.ts (344 lines) =====
  import @deepseek-ai/dsh-settings -> packages/settings/settings/src/index.ts
  import @deepseek-ai/cordis-plugin-loader -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-launch-environment -> packages/util/launch-environment/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-fs -> packages/fs/fs/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./adapter.ts -> packages/llm/llm-pi-ai/src/adapter.ts
  import ./auth.ts -> packages/llm/llm-pi-ai/src/auth.ts
  import ./catalog.ts -> packages/llm/llm-pi-ai/src/catalog.ts
  import ./config.ts -> packages/llm/llm-pi-ai/src/config.ts
  import ./discovery.ts -> packages/llm/llm-pi-ai/src/discovery.ts
  import ./login.ts -> packages/llm/llm-pi-ai/src/login.ts
  import ./provider-data.ts -> packages/llm/llm-pi-ai/src/provider-data.ts
  import ./types.ts -> packages/llm/llm-pi-ai/src/types.ts
  import ./provider.ts -> packages/llm/llm-pi-ai/src/provider.ts
  signals: ctx.on
  fn NS [118-136] (arrow/const)
  fn registrationFacts [125-136] (function)
  fn directoryEntries [149-172] (function)
  fn apply [175-344] (function, exported)

===== packages/llm/llm-pi-ai/src/login.ts (172 lines) =====
  import @earendil-works/pi-ai -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-authorization -> packages/credentials/authorization/src/index.ts
  import @deepseek-ai/dsh-credentials -> packages/credentials/credentials/src/index.ts
  import ./catalog.ts -> packages/llm/llm-pi-ai/src/catalog.ts
  import ./auth.ts -> packages/llm/llm-pi-ai/src/auth.ts
  import ./adapter.ts -> packages/llm/llm-pi-ai/src/adapter.ts
  import ./models.ts -> packages/llm/llm-pi-ai/src/models.ts
  fn loginMethods [40-47] (function)
  fn relay [58-87] (function)
  fn restate [100-120] (function)
  fn registerPiAiFlows [131-172] (function, exported)

===== packages/llm/llm-pi-ai/src/models.ts (92 lines) =====
  import @earendil-works/pi-ai/providers/all -> (external)
  import @earendil-works/pi-ai -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./catalog.ts -> packages/llm/llm-pi-ai/src/catalog.ts
  fn createModels [32-36] (function, exported)
  fn createProvider [43-53] (function, exported)
  fn getSupportedThinkingLevels [60-68] (function, exported)
  fn conversationUpdates [75-92] (function, exported)

===== packages/llm/llm-pi-ai/src/provider-data.ts (19 lines) =====
  import @earendil-works/pi-ai -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./provider-data.generated.ts -> packages/llm/llm-pi-ai/src/provider-data.generated.ts
  fn providerDefaultsOf [12-19] (function, exported)

===== packages/llm/llm-pi-ai/src/provider.ts (192 lines) =====
  import @earendil-works/pi-ai -> (external)
  import @earendil-works/pi-ai/api/anthropic-messages.lazy -> (external)
  import @earendil-works/pi-ai/api/openai-completions.lazy -> (external)
  import @earendil-works/pi-ai/api/openai-responses.lazy -> (external)
  import ./catalog.ts -> packages/llm/llm-pi-ai/src/catalog.ts
  import ./models.ts -> packages/llm/llm-pi-ai/src/models.ts
  fn supportedProtocols [61-63] (function, exported)
  fn harnessApiKeyAuth [77-85] (function)
  fn routeAuth [131-135] (function)
  fn reuseCatalogProvider [144-159] (function)
  fn buildProvider [167-192] (function, exported)

===== packages/llm/llm-pi-ai/src/replay.ts (259 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @earendil-works/pi-ai -> (external)
  fn parseArguments [44-54] (function)
  fn emptyPiUsage [57-66] (function)
  fn toPiReplayState [77-110] (function, exported)
  fn invalidReplay [112-114] (function)
  fn readReplayState [117-149] (function)
  fn foreignAssistant [152-184] (function)
  fn replayedAssistant [187-232] (function)
  fn toPiAssistant [247-259] (function, exported)

===== packages/llm/llm-pi-ai/src/stream.ts (244 lines) =====
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @earendil-works/pi-ai/utils/overflow -> (external)
  import @earendil-works/pi-ai -> (external)
  import ./replay.ts -> packages/llm/llm-pi-ai/src/replay.ts
  fn mapUsage [24-32] (function, exported)
  fn classifyPiAiError [42-68] (function)
  fn mapStopReason [80-128] (function, exported)
  fn toStreamChunks [144-244] (function, exported)

===== packages/llm/llm-pi-ai/src/types.ts (10 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts

===== packages/llm/llm-pi-ai/tsconfig.json (54 lines) =====

===== packages/llm/llm-retry/README.md (149 lines) =====

===== packages/llm/llm-retry/package.json (69 lines) =====

===== packages/llm/llm-retry/src/index.ts (257 lines) =====
  import node:crypto -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import zod -> (external)
  import @deepseek-ai/dsh-agent -> packages/core/agent/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-session-projection -> packages/session/session-projection/src/index.ts
  import ./brand.ts -> packages/llm/llm-retry/src/brand.ts
  import ./types.ts -> packages/llm/llm-retry/src/types.ts
  signals: ctx.effect, ctx.on
  fn validateConfig [30-37] (function)
  fn settleDownstream [49-57] (function)
  fn localDelay [59-64] (function)
  fn retryPolicyKey [66-77] (function)
  fn retryStateKey [79-81] (function)
  fn cancellableDelay [83-96] (function)
  fn apply [120-257] (function, exported)

===== packages/llm/llm-retry/tsconfig.json (36 lines) =====

===== packages/llm/llm-retry/tsdown.config.ts (15 lines) =====
  import tsdown -> (external)

===== packages/llm/plugin-package-inventory-deepseek/README.md (78 lines) =====

===== packages/llm/plugin-package-inventory-deepseek/package.json (65 lines) =====

===== packages/llm/plugin-package-inventory-deepseek/src/index.ts (214 lines) =====
  import node:fs -> (external)
  import node:module -> (external)
  import node:path -> (external)
  import node:url -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/cordis-plugin-loader -> (external)
  import @deepseek-ai/dsh-agent -> packages/core/agent/src/index.ts
  import @deepseek-ai/dsh-deepseek-llm-api-extensions -> packages/llm/deepseek-llm-api-extensions/src/index.ts
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-agent-preset-registry -> packages/preset/agent-preset-registry/src/index.ts
  import @deepseek-ai/dsh-app-boot -> packages/boot/app-boot/src/index.ts
  import ./types.ts -> packages/llm/plugin-package-inventory-deepseek/src/types.ts
  class PackageIdentityResolver [100-134]
  fn barePackageName [55-60] (function)
  fn identityFromManifest [63-69] (function)
  fn barePackageManifest [72-85] (function)
  fn nearestManifest [88-97] (function)
  fn activeEntries [137-146] (function)
  fn compareWireText [149-151] (function)
  fn collectActivePluginPackages [154-192] (function)
  fn apply [199-214] (function, exported)

===== packages/llm/plugin-package-inventory-deepseek/src/types.ts (19 lines) =====

===== packages/llm/plugin-package-inventory-deepseek/tsconfig.json (39 lines) =====

===== packages/llm/token-meter/README.md (163 lines) =====

===== packages/llm/token-meter/package.json (63 lines) =====

===== packages/llm/token-meter/src/breakdown-projection.ts (184 lines) =====
  import zod -> (external)
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-session-projection -> packages/session/session-projection/src/index.ts
  import @deepseek-ai/dsh-compaction -> packages/compaction/compaction/src/index.ts
  import ./estimate.ts -> packages/llm/token-meter/src/estimate.ts
  import ./projection.ts -> packages/llm/token-meter/src/projection.ts
  fn placeSurfaceEvent [73-115] (function)
  fn withTotals [118-126] (function)
  fn withoutClaim [129-133] (function)

===== packages/llm/token-meter/src/estimate.ts (102 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  fn estimateStructuralBlock [29-35] (function, exported)
  fn estimateContent [42-63] (function, exported)
  fn estimateSystemMessage [73-80] (function, exported)
  fn estimateMessage [88-91] (function, exported)
  fn estimateToolsTokens [99-102] (function, exported)

===== packages/llm/token-meter/src/index.ts (296 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-compaction-image-offload/projection -> packages/compaction/compaction-image-offload/src/projection.ts
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-session-projection -> packages/session/session-projection/src/index.ts
  import ./types.ts -> packages/llm/token-meter/src/types.ts
  import ./breakdown-projection.ts -> packages/llm/token-meter/src/breakdown-projection.ts
  import ./usage-projection.ts -> packages/llm/token-meter/src/usage-projection.ts
  import ./estimate.ts -> packages/llm/token-meter/src/estimate.ts
  import ./measurement-projection.ts -> packages/llm/token-meter/src/measurement-projection.ts
  import ./surface-fold.ts -> packages/llm/token-meter/src/surface-fold.ts
  import ./route-pricing.ts -> packages/llm/token-meter/src/route-pricing.ts
  signals: extends Service, ctx.on
  class TokenMeter [87-294] extends Service
  fn usageTokens [57-62] (function)
  fn optionalHeaderEquals [65-71] (function)
  fn validateConfigKeys [74-78] (function)

===== packages/llm/token-meter/src/measurement-projection.ts (100 lines) =====
  import zod -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-session-projection -> packages/session/session-projection/src/index.ts
  import ./estimate.ts -> packages/llm/token-meter/src/estimate.ts
  fn advanceMeasurement [44-82] (function, exported)

===== packages/llm/token-meter/src/projection.ts (79 lines) =====
  import @deepseek-ai/dsh-session-projection/types -> packages/session/session-projection/src/types.ts

===== packages/llm/token-meter/src/route-pricing.ts (76 lines) =====
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./estimate.ts -> packages/llm/token-meter/src/estimate.ts
  import ./surface-fold.ts -> packages/llm/token-meter/src/surface-fold.ts
  import ./types.ts -> packages/llm/token-meter/src/types.ts
  fn priceSurface [32-76] (function, exported)

===== packages/llm/token-meter/src/surface-fold.ts (142 lines) =====
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import ./estimate.ts -> packages/llm/token-meter/src/estimate.ts
  fn collectProjectedAttachments [53-70] (function)
  fn analyzeNode [73-96] (function)
  fn planSurfaceTokens [107-128] (function, exported)
  fn commitSurfaceTokens [136-142] (function, exported)

===== packages/llm/token-meter/src/surface-projection.ts (96 lines) =====
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-compaction -> packages/compaction/compaction/src/index.ts
  import ./estimate.ts -> packages/llm/token-meter/src/estimate.ts
  fn foldSurfaceProjection [64-96] (function, exported)

===== packages/llm/token-meter/src/turn-usage.ts (274 lines) =====
  import @deepseek-ai/dsh-llm/assistant-stream -> packages/llm/llm/src/assistant-stream.ts
  import @deepseek-ai/dsh-llm/types -> packages/llm/llm/src/types.ts
  import @deepseek-ai/dsh-llm-retry/types -> packages/llm/llm-retry/src/types.ts
  import @deepseek-ai/dsh-session/types -> packages/core/session/src/types.ts
  fn isCount [59-61] (function)
  fn safeSum [63-70] (function)
  fn messageRoute [72-75] (function)
  fn streamUsage [77-79] (function)
  fn normalizeUsage [81-124] (function)
  fn aggregateAttempts [126-159] (function)
  fn sameAttempt [161-167] (function)
  fn deriveTurnTokenUsage [178-274] (function, exported)

===== packages/llm/token-meter/src/usage-projection.ts (213 lines) =====
  import zod -> (external)
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-llm-retry/types -> packages/llm/llm-retry/src/types.ts
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-session-projection -> packages/session/session-projection/src/index.ts
  import ./projection.ts -> packages/llm/token-meter/src/projection.ts
  import ./surface-projection.ts -> packages/llm/token-meter/src/surface-projection.ts
  fn zeroBuckets [14-19] (arrow/const)
  fn bucketsFrom [21-26] (arrow/const)
  fn bucketsEqual [28-28] (arrow/const)
  fn addReplacing [34-43] (arrow/const)
  fn pressureFrom [78-78] (arrow/const)
  fn usageOf [82-86] (function)

===== packages/llm/token-meter/tsconfig.json (39 lines) =====

===== packages/shell/README.md (51 lines) =====

===== packages/shell/bash-local/README.md (152 lines) =====

===== packages/shell/bash-local/package.json (47 lines) =====

===== packages/shell/bash-local/src/index.ts (404 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  class LocalBashExecutor [97-402] extends ShellExecutor
  fn finalOutput [57-64] (function)
  fn assertPositiveFinite [66-70] (function)
  fn assertServiceableBashConfig [79-88] (function, exported)

===== packages/shell/bash-local/tsconfig.json (33 lines) =====

===== packages/shell/bash-sandbox/README.md (183 lines) =====

===== packages/shell/bash-sandbox/package.json (49 lines) =====

===== packages/shell/bash-sandbox/src/helpers.ts (14 lines) =====
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  fn classifyDenial [12-14] (function, exported)

===== packages/shell/bash-sandbox/src/index.ts (192 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-bash-local -> packages/shell/bash-local/src/index.ts
  import ./helpers.ts -> packages/shell/bash-sandbox/src/helpers.ts
  class SandboxBashExecutor [45-190] extends LocalBashExecutor

===== packages/shell/bash-sandbox/tsconfig.json (39 lines) =====

===== packages/shell/pwsh-local/README.md (161 lines) =====

===== packages/shell/pwsh-local/package.json (47 lines) =====

===== packages/shell/pwsh-local/src/index.ts (449 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import ./resolve.ts -> packages/shell/pwsh-local/src/resolve.ts
  class PwshLocalExecutor [123-446] extends ShellExecutor
  fn finalOutput [85-92] (function)
  fn assertPositiveFinite [94-98] (function)
  fn assertServiceablePwshConfig [107-116] (function, exported)

===== packages/shell/pwsh-local/tsconfig.json (33 lines) =====

===== packages/shell/pwsh-sandbox/README.md (152 lines) =====

===== packages/shell/pwsh-sandbox/package.json (48 lines) =====

===== packages/shell/pwsh-sandbox/src/helpers.ts (120 lines) =====
  import node:fs -> (external)
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  fn isUsableWorkdir [18-26] (function)
  fn isRunnerSpawnFailure [42-56] (function, exported)
  fn classifyDenial [70-72] (function, exported)
  fn classifyRunnerFailure [84-106] (function, exported)
  fn matchesSignature [115-119] (function, exported)

===== packages/shell/pwsh-sandbox/src/index.ts (200 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-pwsh-local -> packages/shell/pwsh-local/src/index.ts
  import ./helpers.ts -> packages/shell/pwsh-sandbox/src/helpers.ts
  class SandboxPwshExecutor [52-197] extends PwshLocalExecutor

===== packages/shell/shell/README.md (146 lines) =====

===== packages/shell/shell/package.json (39 lines) =====

===== packages/shell/shell/src/index.ts (96 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import ./types.ts -> packages/shell/shell/src/types.ts
  import ./render.ts -> packages/shell/shell/src/render.ts
  signals: extends Service
  class ShellExecutor [64-94] extends Service

===== packages/shell/shell/src/types.ts (238 lines) =====
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts

===== packages/shell/shell/tsconfig.json (24 lines) =====

===== packages/shell/shell-env/README.md (139 lines) =====

===== packages/shell/shell-env/package.json (50 lines) =====

===== packages/shell/shell-env/src/index.ts (211 lines) =====
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-home-paths -> packages/util/home-paths/src/index.ts
  import @deepseek-ai/dsh-tools -> packages/core/tools/src/index.ts
  import @deepseek-ai/dsh-app-boot -> packages/boot/app-boot/src/index.ts
  signals: extends Service, ctx.effect
  class ShellEnvRegistry [93-202] extends Service
  fn apply [209-211] (function, exported)

===== packages/shell/shell-env/tsconfig.json (33 lines) =====

===== packages/shell/tool-bash/README.md (229 lines) =====

===== packages/shell/tool-bash/package.json (75 lines) =====

===== packages/shell/tool-bash/src/background.ts (129 lines) =====
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-jobs -> packages/jobs/jobs/src/index.ts
  fn sandboxNotes [21-31] (function)
  fn processOutcome [44-55] (function, exported)
  fn processSources [67-76] (function, exported)
  fn ringDelta [86-91] (function, exported)
  fn processJob [99-129] (function, exported)

===== packages/shell/tool-bash/src/index.ts (556 lines) =====
  import @deepseek-ai/dsh-working-directory -> packages/session/working-directory/src/index.ts
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import node:path -> (external)
  import @deepseek-ai/dsh-tools -> packages/core/tools/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-jobs -> packages/jobs/jobs/src/index.ts
  import @deepseek-ai/dsh-user-approval -> packages/interaction/user-approval/src/index.ts
  import @deepseek-ai/dsh-shell-env -> packages/shell/shell-env/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import ./background.ts -> packages/shell/tool-bash/src/background.ts
  import ./render.ts -> packages/shell/tool-bash/src/render.ts
  fn validateBashArgs [73-88] (function)
  fn bashDescription [90-99] (function)
  fn presentBashCall [108-124] (function)
  fn presentBashResult [130-143] (function)
  fn resolveWorkdir [146-152] (function)
  fn canonicalBashResult [155-179] (function)
  fn toolAborted [182-186] (function)
  fn apply [202-556] (function, exported)

===== packages/shell/tool-bash/src/render.ts (126 lines) =====
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  fn streamText [12-15] (function)
  fn renderResult [28-66] (function, exported)
  fn renderPromoted [77-82] (function, exported)
  fn renderJobRead [97-118] (function, exported)

===== packages/shell/tool-bash/tsconfig.json (54 lines) =====

===== packages/shell/tool-bash-persistent/README.md (161 lines) =====

===== packages/shell/tool-bash-persistent/package.json (64 lines) =====

===== packages/shell/tool-bash-persistent/src/index.ts (487 lines) =====
  import @deepseek-ai/dsh-working-directory -> packages/session/working-directory/src/index.ts
  import node:crypto -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-agent -> packages/core/agent/src/index.ts
  import @deepseek-ai/dsh-output-retention -> packages/util/output-retention/src/index.ts
  import @deepseek-ai/dsh-terminal -> packages/terminal/terminal/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import @deepseek-ai/dsh-tools -> packages/core/tools/src/index.ts
  signals: ctx.effect
  fn maybeTruncate [59-64] (function)
  fn markers [66-72] (function)
  fn quoteForBash [74-80] (function)
  fn wrapCommand [82-87] (function)
  fn trimTrailingNewline [89-91] (function)
  fn commandOutput [93-108] (function)
  fn partialOutput [110-133] (function)
  fn pause [135-137] (function)
  fn nextScrollbackOffset [139-142] (function)
  fn retainedScrollback [144-163] (function)
  fn renderCaptured [165-174] (function)
  fn appendStatusMarker [176-179] (function)
  fn renderShellExitStatus [181-192] (function)
  fn respondToSessionExit [201-222] (function)
  fn persistentShells [224-298] (function)
  fn executeCommand [300-393] (function)
  fn registerPersistentBash [400-441] (function)
  fn apply [467-487] (function, exported)

===== packages/shell/tool-bash-persistent/tsconfig.json (36 lines) =====

===== packages/shell/tool-pwsh/README.md (220 lines) =====

===== packages/shell/tool-pwsh/package.json (74 lines) =====

===== packages/shell/tool-pwsh/src/background.ts (132 lines) =====
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-jobs -> packages/jobs/jobs/src/index.ts
  fn sandboxNotes [23-33] (function)
  fn processOutcome [46-57] (function, exported)
  fn processSources [69-78] (function, exported)
  fn ringDelta [88-93] (function, exported)
  fn processJob [101-131] (function, exported)

===== packages/shell/tool-pwsh/src/index.ts (615 lines) =====
  import node:path -> (external)
  import @deepseek-ai/dsh-working-directory -> packages/session/working-directory/src/index.ts
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-tools -> packages/core/tools/src/index.ts
  import @deepseek-ai/dsh-llm -> packages/llm/llm/src/index.ts
  import @deepseek-ai/dsh-jobs -> packages/jobs/jobs/src/index.ts
  import @deepseek-ai/dsh-shell-env -> packages/shell/shell-env/src/index.ts
  import @deepseek-ai/dsh-user-approval -> packages/interaction/user-approval/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import ./background.ts -> packages/shell/tool-pwsh/src/background.ts
  import ./render.ts -> packages/shell/tool-pwsh/src/render.ts
  fn validatePwshArgs [107-118] (function)
  fn pwshDescription [121-149] (function)
  fn resolveWorkdir [152-158] (function)
  fn canonicalPwshResult [161-187] (function)
  fn toolAborted [190-194] (function)
  fn apply [212-615] (function, exported)

===== packages/shell/tool-pwsh/src/render.ts (139 lines) =====
  import @deepseek-ai/dsh-shell -> packages/shell/shell/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  fn streamText [20-23] (function)
  fn renderPwshResult [48-86] (function, exported)
  fn renderPwshPromoted [97-102] (function, exported)
  fn renderPwshJobRead [117-138] (function, exported)

===== packages/shell/tool-pwsh/tsconfig.json (57 lines) =====

===== packages/shell/tool-pwsh-persistent/README.md (167 lines) =====

===== packages/shell/tool-pwsh-persistent/package.json (65 lines) =====

===== packages/shell/tool-pwsh-persistent/src/index.ts (500 lines) =====
  import @deepseek-ai/dsh-working-directory -> packages/session/working-directory/src/index.ts
  import node:crypto -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-agent -> packages/core/agent/src/index.ts
  import @deepseek-ai/dsh-output-retention -> packages/util/output-retention/src/index.ts
  import @deepseek-ai/dsh-terminal -> packages/terminal/terminal/src/index.ts
  import @deepseek-ai/dsh-timeout -> packages/util/timeout/src/index.ts
  import @deepseek-ai/dsh-tools -> packages/core/tools/src/index.ts
  signals: ctx.effect
  fn maybeTruncate [58-63] (function)
  fn markers [65-71] (function)
  fn quoteForPwsh [82-90] (function)
  fn wrapCommand [92-100] (function)
  fn trimTrailingNewline [102-104] (function)
  fn commandOutput [106-129] (function)
  fn partialOutput [131-155] (function)
  fn pause [157-159] (function)
  fn nextScrollbackOffset [161-164] (function)
  fn retainedScrollback [166-185] (function)
  fn renderCaptured [187-196] (function)
  fn appendStatusMarker [198-201] (function)
  fn renderShellExitStatus [203-214] (function)
  fn respondToSessionExit [223-245] (function)
  fn persistentShells [247-308] (function)
  fn executeCommand [310-404] (function)
  fn registerPersistentPwsh [411-452] (function)
  fn apply [478-498] (function, exported)

===== packages/shell/tool-pwsh-persistent/tsconfig.json (36 lines) =====

===== packages/subprocess/README.md (51 lines) =====

===== packages/subprocess/subprocess/README.md (163 lines) =====

===== packages/subprocess/subprocess/package.json (43 lines) =====

===== packages/subprocess/subprocess/src/control.ts (24 lines) =====
  import node:net -> (external)
  import node:stream -> (external)
  fn openInheritedControlChannel [19-24] (function, exported)

===== packages/subprocess/subprocess/tsconfig.json (24 lines) =====

===== packages/subprocess/subprocess/tsdown.config.ts (15 lines) =====
  import tsdown -> (external)

===== packages/subprocess/subprocess-local/README.md (168 lines) =====

===== packages/subprocess/subprocess-local/package.json (63 lines) =====

===== packages/subprocess/subprocess-local/src/bin.ts (25 lines) =====
  import ./runner-launch.ts -> packages/subprocess/subprocess-local/src/runner-launch.ts
  import ./spawn-runner.ts -> packages/subprocess/subprocess-local/src/spawn-runner.ts
  fn runSelectedSubprocessRunner [10-16] (function, exported)

===== packages/subprocess/subprocess-local/src/control-spawn.ts (35 lines) =====
  import @deepseek-ai/dsh-subprocess/control -> packages/subprocess/subprocess/src/control.ts
  import node:stream -> (external)
  fn controlPipe [12-19] (function, exported)
  fn controlEnvironment [27-35] (function, exported)

===== packages/subprocess/subprocess-local/src/linux-execve.ts (79 lines) =====
  import node:util -> (external)
  import @deepseek-ai/dsh-subprocess/control -> packages/subprocess/subprocess/src/control.ts
  import @deepseek-ai/dsh-lazy-require -> packages/util/lazy-require/src/index.ts
  import koffi -> (external)
  fn systemError [32-43] (function)
  fn loadLinuxExecve [49-79] (function, exported)

===== packages/subprocess/subprocess-local/src/linux-scope-selector.ts (101 lines) =====
  import ./linux-scope.ts -> packages/subprocess/subprocess-local/src/linux-scope.ts
  class LinuxScopeSelector [53-101]

===== packages/subprocess/subprocess-local/src/linux-scope.ts (724 lines) =====
  import ./control-spawn.ts -> packages/subprocess/subprocess-local/src/control-spawn.ts
  import node:child_process -> (external)
  import node:crypto -> (external)
  import node:fs -> (external)
  import node:path -> (external)
  import node:timers/promises -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import ./linux-execve.ts -> packages/subprocess/subprocess-local/src/linux-execve.ts
  import ./managed-owner.ts -> packages/subprocess/subprocess-local/src/managed-owner.ts
  import ./runner-protocol.ts -> packages/subprocess/subprocess-local/src/runner-protocol.ts
  import ./runner-launch.ts -> packages/subprocess/subprocess-local/src/runner-launch.ts
  import ./spawn.ts -> packages/subprocess/subprocess-local/src/spawn.ts
  class LinuxScopeNotStartedError [262-264] extends Error
  class LinuxScopeStartup [266-282]
  class SystemdScopeOwner [284-540] implements BoundProcessOwner
  fn managerEnvironment [69-73] (function)
  fn quietSystemdEnvironment [75-77] (function)
  fn querySystemctl [79-95] (function)
  fn unitStem [97-99] (function)
  fn sleepWithAbort [101-103] (function)
  fn probeLinuxBootstrap [110-119] (function, exported)
  fn probeLinuxScope [126-155] (function, exported)
  fn probeLinuxNative [162-164] (function, exported)
  fn probeLinuxManager [171-179] (function, exported)
  fn unixSocketListener [186-203] (function)
  fn linuxManagerListener [212-216] (function, exported)
  fn systemdRunIdentity [224-240] (function, exported)
  fn confirmLinuxManager [249-251] (function, exported)
  fn scopeArgs [542-560] (function)
  fn directOutcome [562-585] (function)
  fn signalLinuxDirectProcess [593-603] (function, exported)
  fn signalChildGroup [605-614] (function)
  fn prepareLinuxTerminalScope [635-662] (function, exported)
  fn launchLinuxScope [672-724] (function, exported)

===== packages/subprocess/subprocess-local/src/managed-owner.ts (56 lines) =====
  import node:stream -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  fn waitWithAbort [39-56] (function, exported)

===== packages/subprocess/subprocess-local/src/output.ts (313 lines) =====
  import node:crypto -> (external)
  import node:fs -> (external)
  import node:path -> (external)
  import node:os -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  class OutputCollector [129-313]
  fn privateSpillDir [42-45] (function)
  fn reportSpillFailureToStderr [65-67] (function)
  fn logSpillFailure [77-86] (function, exported)
  fn prepareManagedProcessBinding [104-111] (function, exported)

===== packages/subprocess/subprocess-local/src/runner-launch.ts (315 lines) =====
  import node:child_process -> (external)
  import node:fs -> (external)
  import node:path -> (external)
  import node:util -> (external)
  import node:url -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import ./spawn.ts -> packages/subprocess/subprocess-local/src/spawn.ts
  import ./control-spawn.ts -> packages/subprocess/subprocess-local/src/control-spawn.ts
  import @deepseek-ai/dsh-subprocess/control -> packages/subprocess/subprocess/src/control.ts
  fn spawnRunnerInvocation [29-42] (function, exported)
  fn runnerInvocationAvailable [49-60] (function, exported)
  fn runnerEnvironment [68-86] (function, exported)
  fn consumeRunnerSelection [93-97] (function, exported)
  fn parseRunnerTargetArgv [104-109] (function, exported)
  fn runnerStdio [119-147] (function, exported)
  fn windowsEnvironmentValue [149-157] (function)
  fn executableCandidateExists [159-170] (function)
  fn windowsPathDirectories [172-194] (function)
  fn windowsFileNameStart [196-200] (function)
  fn windowsSearchPathJoin [202-229] (function)
  fn windowsExecutableNames [231-240] (function)
  fn resolveWindowsExecutable [252-282] (function, exported)
  fn throwNullByteError [284-289] (function)
  fn validateNoNullByte [291-293] (function)
  fn targetEnvironment [300-315] (function, exported)

===== packages/subprocess/subprocess-local/src/runner-protocol.ts (273 lines) =====
  import node:fs -> (external)
  import node:os -> (external)
  import node:path -> (external)
  fn isRecord [61-63] (function)
  fn hasExactKeys [65-69] (function)
  fn isStringRecord [71-73] (function)
  fn isSerializedRunnerError [75-86] (function)
  fn parseErrorResult [88-96] (function)
  fn createLinuxLaunchFiles [103-118] (function, exported)
  fn linuxLaunchFilesFromLocator [125-131] (function, exported)
  fn consumeLinuxLaunchRequest [138-148] (function, exported)
  fn writeLinuxStartupError [155-157] (function, exported)
  fn readLinuxStartupError [164-169] (function, exported)
  fn parseWindowsStartRequest [176-183] (function, exported)
  fn isWindowsTerminateRequest [190-192] (function, exported)
  fn parseWindowsRunnerResult [199-217] (function, exported)
  fn serializeRunnerError [224-234] (function, exported)
  fn deserializeRunnerError [241-249] (function, exported)
  fn cleanupLinuxLaunchFiles [255-273] (function, exported)

===== packages/subprocess/subprocess-local/src/shell-activity.ts (131 lines) =====
  import node:fs -> (external)
  import node:os -> (external)
  import node:path -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  class ShellActivity [10-51]
  fn quote [7-51] (function)
  fn prepareShellActivity [60-131] (function, exported)

===== packages/subprocess/subprocess-local/src/spawn-runner.ts (490 lines) =====
  import @deepseek-ai/dsh-subprocess/control -> packages/subprocess/subprocess/src/control.ts
  import node:fs -> (external)
  import @deepseek-ai/dsh-win32-process -> packages/subprocess/win32-process/src/index.ts
  import ./linux-execve.ts -> packages/subprocess/subprocess-local/src/linux-execve.ts
  import ./runner-protocol.ts -> packages/subprocess/subprocess-local/src/runner-protocol.ts
  import ./runner-launch.ts -> packages/subprocess/subprocess-local/src/runner-launch.ts
  class WindowsJobRunner [225-440]
  fn nodeSpawnError [80-93] (function)
  fn asSpawnError [95-110] (function)
  fn windowsPathNotFoundError [112-114] (function)
  fn windowsStartCancelledError [116-121] (function)
  fn linuxPathNotFoundError [123-131] (function)
  fn execLinuxFile [133-148] (function)
  fn execLinuxTarget [150-177] (function)
  fn runLinux [179-204] (function)
  fn sendMessage [206-223] (function)
  fn runSpawnRunner [449-462] (function, exported)
  fn reportSpawnRunnerFailure [470-490] (function, exported)

===== packages/subprocess/subprocess-local/src/windows-job.ts (247 lines) =====
  import ./control-spawn.ts -> packages/subprocess/subprocess-local/src/control-spawn.ts
  import node:child_process -> (external)
  import node:fs -> (external)
  import node:os -> (external)
  import node:stream -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-win32-process -> packages/subprocess/win32-process/src/index.ts
  import ./managed-owner.ts -> packages/subprocess/subprocess-local/src/managed-owner.ts
  import ./runner-protocol.ts -> packages/subprocess/subprocess-local/src/runner-protocol.ts
  import ./runner-launch.ts -> packages/subprocess/subprocess-local/src/runner-launch.ts
  class WindowsJobOwner [70-116] implements BoundProcessOwner
  fn isWindowsStartCancellationError [44-50] (function)
  fn probeWindowsJob [57-68] (function, exported)
  fn launchWindowsJob [125-247] (function, exported)

===== packages/subprocess/subprocess-local/tsconfig.json (30 lines) =====

===== packages/subprocess/subprocess-local/tsdown.config.ts (16 lines) =====
  import tsdown -> (external)

===== packages/subprocess/win32-process/README.md (89 lines) =====

===== packages/subprocess/win32-process/package.json (39 lines) =====

===== packages/subprocess/win32-process/src/control-stdio.ts (47 lines) =====
  import ./ffi.ts -> packages/subprocess/win32-process/src/ffi.ts
  fn inheritedControlStdio [29-47] (function, exported)

===== packages/subprocess/win32-process/src/koffi.ts (10 lines) =====
  import koffi -> (external)
  import @deepseek-ai/dsh-lazy-require -> packages/util/lazy-require/src/index.ts

===== packages/subprocess/win32-process/tsconfig.json (16 lines) =====

===== packages/terminal/README.md (53 lines) =====

===== packages/terminal/terminal/README.md (151 lines) =====

===== packages/terminal/terminal/package.json (43 lines) =====

===== packages/terminal/terminal-bash/README.md (183 lines) =====

===== packages/terminal/terminal-bash/package.json (60 lines) =====

===== packages/terminal/terminal-bash/src/config.ts (142 lines) =====
  import @deepseek-ai/schemastery -> (external)
  import @deepseek-ai/dsh-pwsh-local -> packages/shell/pwsh-local/src/index.ts
  fn resolveConfig [78-90] (function, exported)
  fn validateConfig [119-142] (function, exported)

===== packages/terminal/terminal-bash/src/index.ts (235 lines) =====
  import @deepseek-ai/dsh-working-directory -> packages/session/working-directory/src/index.ts
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-agent -> packages/core/agent/src/index.ts
  import @deepseek-ai/dsh-session -> packages/core/session/src/index.ts
  import @deepseek-ai/dsh-terminal -> packages/terminal/terminal/src/index.ts
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-pwsh-local -> packages/shell/pwsh-local/src/index.ts
  import ./config.ts -> packages/terminal/terminal-bash/src/config.ts
  import ./session.ts -> packages/terminal/terminal-bash/src/session.ts
  import ./sanitize.ts -> packages/terminal/terminal-bash/src/sanitize.ts
  signals: ctx.on
  class BashTerminalBackend [181-228] implements TerminalBackend
  fn ensureSandboxModeFence [36-59] (function)
  fn childEnvironment [61-86] (function)
  fn spawnArgv [97-106] (function)
  fn startupSession [111-168] (function)
  fn rejectAfterStartupCleanup [171-178] (function)
  fn apply [231-235] (function, exported)

===== packages/terminal/terminal-bash/src/session.ts (793 lines) =====
  import node:buffer -> (external)
  import @xterm/headless -> (external)
  import @deepseek-ai/dsh-lazy-require -> packages/util/lazy-require/src/index.ts
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-terminal -> packages/terminal/terminal/src/index.ts
  import ./config.ts -> packages/terminal/terminal-bash/src/config.ts
  import ./sanitize.ts -> packages/terminal/terminal-bash/src/sanitize.ts
  class BoundedTextBuffer [54-156]
  class LocalSendOperation [158-234] implements TerminalSendOperation
  class LocalPtySession [237-793] implements TerminalBackendSession
  fn utf8Tail [30-42] (function)

===== packages/terminal/terminal-bash/tsconfig.json (48 lines) =====

===== packages/ssh/README.md (45 lines) =====

===== packages/ssh/fs-ssh/README.md (81 lines) =====

===== packages/ssh/fs-ssh/package.json (49 lines) =====

===== packages/ssh/fs-ssh/src/index.ts (126 lines) =====
  import node:path -> (external)
  import node:url -> (external)
  import @deepseek-ai/dsh-fs -> packages/fs/fs/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-ssh -> packages/ssh/ssh/src/index.ts
  import @deepseek-ai/dsh-ssh/protocol -> packages/ssh/ssh/src/protocol.ts
  import @deepseek-ai/dsh-ssh/schemas -> packages/ssh/ssh/src/schemas.ts
  import zod -> (external)
  class SshFileSystem [16-124] extends FileSystem

===== packages/ssh/fs-ssh/tsconfig.json (30 lines) =====

===== packages/ssh/sandbox-ssh/README.md (78 lines) =====

===== packages/ssh/sandbox-ssh/package.json (45 lines) =====

===== packages/ssh/sandbox-ssh/src/index.ts (33 lines) =====
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import @deepseek-ai/dsh-ssh -> packages/ssh/ssh/src/index.ts
  import zod -> (external)
  class SshSandboxProvider [10-31] extends SandboxProvider

===== packages/ssh/sandbox-ssh/tsconfig.json (24 lines) =====

===== packages/ssh/ssh/README.md (111 lines) =====

===== packages/ssh/ssh/package.json (87 lines) =====

===== packages/ssh/ssh/src/helper-entry.ts (28 lines) =====
  import node:url -> (external)
  import node:sea -> (external)
  import ./helper.ts -> packages/ssh/ssh/src/helper.ts
  fn main [8-26] (function)

===== packages/ssh/ssh/src/helper-processes.ts (456 lines) =====
  import node:crypto -> (external)
  import node:fs/promises -> (external)
  import node:path -> (external)
  import node:net -> (external)
  import node:tls -> (external)
  import node:stream -> (external)
  import node:stream/promises -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-subprocess-local/output -> packages/subprocess/subprocess-local/src/output.ts
  import ./schemas.ts -> packages/ssh/ssh/src/schemas.ts
  import zod -> (external)
  import ./stream-security.ts -> packages/ssh/ssh/src/stream-security.ts
  import ./protocol.ts -> packages/ssh/ssh/src/protocol.ts
  class CollectedOutputForwarder [53-87]
  class RemoteProcesses [90-456]
  fn closeEndpoint [41-50] (function)

===== packages/ssh/ssh/src/helper.ts (289 lines) =====
  import node:crypto -> (external)
  import node:fs -> (external)
  import node:fs/promises -> (external)
  import node:stream -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import @deepseek-ai/dsh-fs -> packages/fs/fs/src/index.ts
  import @deepseek-ai/dsh-fs-sandbox -> packages/fs/fs-sandbox/src/index.ts
  import @deepseek-ai/dsh-subprocess -> packages/subprocess/subprocess/src/index.ts
  import @deepseek-ai/dsh-subprocess-local -> packages/subprocess/subprocess-local/src/index.ts
  import @deepseek-ai/dsh-sandbox-local -> packages/sandbox/sandbox-local/src/index.ts
  import @deepseek-ai/dsh-sandbox-policy -> packages/sandbox/sandbox-policy/src/index.ts
  import @deepseek-ai/dsh-session-projection -> packages/session/session-projection/src/index.ts
  import @deepseek-ai/dsh-sandbox -> packages/sandbox/sandbox/src/index.ts
  import zod -> (external)
  import ./protocol.ts -> packages/ssh/ssh/src/protocol.ts
  import ./helper-processes.ts -> packages/ssh/ssh/src/helper-processes.ts
  import ./schemas.ts -> packages/ssh/ssh/src/schemas.ts
  fn services [28-36] (function)
  fn runSshHelper [56-289] (function, exported)

===== packages/ssh/ssh/src/index.ts (331 lines) =====
  import node:child_process -> (external)
  import node:fs/promises -> (external)
  import node:path -> (external)
  import node:net -> (external)
  import @deepseek-ai/cordis -> (external)
  import @deepseek-ai/schemastery -> (external)
  import zod -> (external)
  import @deepseek-ai/dsh-util-values -> packages/util/values/src/index.ts
  import ./protocol.ts -> packages/ssh/ssh/src/protocol.ts
  import ./schemas.ts -> packages/ssh/ssh/src/schemas.ts
  import ./stream-security.ts -> packages/ssh/ssh/src/stream-security.ts
  signals: extends Service, ctx.effect
  class SshConnection [59-329] extends Service

===== packages/ssh/ssh/src/protocol.ts (235 lines) =====
  import node:crypto -> (external)
  import node:events -> (external)
  import node:stream -> (external)
  import zod -> (external)
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  class RemoteOperationError [50-55] extends Error
  class SshRpcPeer [58-235] extends EventEmitter
  fn requestClass [25-31] (function)
  fn operationError [45-47] (function)

===== packages/ssh/ssh/src/schemas.ts (123 lines) =====
  import zod -> (external)
  import @deepseek-ai/dsh-fs -> packages/fs/fs/src/index.ts
  import @deepseek-ai/dsh-brand -> packages/util/brand/src/index.ts
  import ./protocol.ts -> packages/ssh/ssh/src/protocol.ts
  fn outputSnapshotFrameLimit [108-110] (function, exported)

===== packages/ssh/ssh/src/stream-security.ts (47 lines) =====
  import node:tls -> (external)
  import node:net -> (external)
  fn authenticateStream [18-47] (function, exported)

===== packages/ssh/ssh/tsconfig.json (51 lines) =====

===== packages/ssh/ssh/tsdown.config.ts (6 lines) =====
  import tsdown -> (external)

===== packages/ssh/ssh-helper-runtime/README.md (107 lines) =====

===== packages/ssh/ssh-helper-runtime/package.json (64 lines) =====

===== packages/ssh/ssh-helper-runtime/src/index.ts (39 lines) =====
  import node:module -> (external)
  import node:fs -> (external)
  import node:path -> (external)
  import node:sea -> (external)
  import node:url -> (external)
  import @deepseek-ai/dsh-ptc-runtime-node/process -> packages/ptc-runtime/ptc-runtime-node/src/process.ts
  import @deepseek-ai/dsh-subprocess-local/runner -> UNRESOLVED:@deepseek-ai/dsh-subprocess-local/runner
  import @deepseek-ai/dsh-ssh/helper -> packages/ssh/ssh/src/helper.ts
  fn runSshHelperRuntime [14-39] (function, exported)

===== packages/ssh/ssh-helper-runtime/tsconfig.json (24 lines) =====

===== packages/ssh/subprocess-ssh/README.md (87 lines) =====
