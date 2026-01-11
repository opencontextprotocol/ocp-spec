## [0.7.1](https://github.com/opencontextprotocol/ocp-spec/compare/v0.7.0...v0.7.1) (2026-01-05)


### Bug Fixes

* add resource_name filter for api-page template ([db52274](https://github.com/opencontextprotocol/ocp-spec/commit/db52274ee3e520a4513b66896410f491cbd419c4))

## [0.7.0](https://github.com/opencontextprotocol/ocp-spec/compare/v0.6.0...v0.7.0) (2026-01-05)


### Features

* bump registry to v0.8.0 ([d942bff](https://github.com/opencontextprotocol/ocp-spec/commit/d942bff13c937bf4bf5894903e127b95d3a04b34))

## [0.6.0](https://github.com/opencontextprotocol/ocp-spec/compare/v0.5.0...v0.6.0) (2026-01-05)


### Features

* add build scripts for registry content ([e1ca417](https://github.com/opencontextprotocol/ocp-spec/commit/e1ca41790cb249c4d3bb70f7bb9adccb4652ed8c))


### Bug Fixes

* streamline http descriptions in launch.md ([605bbed](https://github.com/opencontextprotocol/ocp-spec/commit/605bbed9a1d5775536ff1257b9d5f0ba81b58595))

## [0.5.0](https://github.com/opencontextprotocol/ocp-spec/compare/v0.4.0...v0.5.0) (2026-01-04)


### Features

* update registry version to v0.6.0 ([ca4419d](https://github.com/opencontextprotocol/ocp-spec/commit/ca4419d85fdb18a418b1cfcfd6ac52f4395e40b6))

## [0.4.0](https://github.com/opencontextprotocol/ocp-spec/compare/v0.3.0...v0.4.0) (2026-01-04)


### Features

* add registry version argument for content generation ([71a0b91](https://github.com/opencontextprotocol/ocp-spec/commit/71a0b912f98babb9e1e41e061a1ddebce6484949))

## [0.3.0](https://github.com/opencontextprotocol/ocp-spec/compare/v0.2.0...v0.3.0) (2026-01-04)


### Features

* enable llms output format ([feb7516](https://github.com/opencontextprotocol/ocp-spec/commit/feb7516d24dddd5371c4b88345fd939ed9a3074a))

## [0.2.0](https://github.com/opencontextprotocol/ocp-spec/compare/v0.1.2...v0.2.0) (2026-01-03)


### Features

* add blog launch post and update configuration ([c9f40e4](https://github.com/opencontextprotocol/ocp-spec/commit/c9f40e4bbd61790d246be5b421fc91855f493291))

## [0.1.2](https://github.com/opencontextprotocol/ocp-spec/compare/v0.1.1...v0.1.2) (2026-01-02)


### Bug Fixes

* update registry titles and links ([e6cb6c2](https://github.com/opencontextprotocol/ocp-spec/commit/e6cb6c2025a0f2b7d3a172cd98302cb0e542e9c3))

## [0.1.1](https://github.com/opencontextprotocol/ocp-spec/compare/v0.1.0...v0.1.1) (2026-01-02)


### Bug Fixes

* update broken api-registry links to registry-client ([f4dd1ea](https://github.com/opencontextprotocol/ocp-spec/commit/f4dd1eaef796da307543c6c0e72faab855bf6eb2))

## [0.1.0](https://github.com/opencontextprotocol/ocp-spec/compare/5ba6397f87d41fb8d3b9c2b61b990eb437c841ce...v0.1.0) (2026-01-02)


### ⚠ BREAKING CHANGES

* **python:** convenience functions for specific APIs removed
All 67 tests passing with 70% coverage
* removed CLI from ocp-python library package
* Enhanced OCP with automatic API discovery capabilities

- feat(spec): add deterministic tool naming convention
- feat(spec): add API registration and discovery process documentation
- feat(spec): add reference implementation testing standards
- feat(python): implement OCPSchemaDiscovery for OpenAPI parsing
- feat(python): implement OCPAgent combining context + discovery
- feat(python): add deterministic tool naming (operationId or method_path)
- test: add 73 comprehensive tests with 84-100% coverage
- refactor: clean architecture separation (context, discovery, agent)
- docs: update examples with simplified main.py structure

Provides complete MCP alternative with zero infrastructure overhead
* First release of Python client library

Co-authored-by: OCP Contributors <hello@opencontextprotocol.org>

### Features

* add .gitignore and LICENSE files, update pyproject.toml ([1dd23f4](https://github.com/opencontextprotocol/ocp-spec/commit/1dd23f47b92043b065011dfabf096207bcea150e))
* add .python-version file for version management ([e71062a](https://github.com/opencontextprotocol/ocp-spec/commit/e71062a40018be2567be0e7730a814d1a7da9e7c))
* add agent context documentation and improve clarity ([9f50c87](https://github.com/opencontextprotocol/ocp-spec/commit/9f50c87c73bd40083909657715a8a49d4da1a08f))
* add agent context documentation and project standards ([0241f58](https://github.com/opencontextprotocol/ocp-spec/commit/0241f581f97536607f96ee118c6d8fb730a8a610))
* add API registry, context, IDE integration, and tool discovery documentation ([18cf21a](https://github.com/opencontextprotocol/ocp-spec/commit/18cf21ad0064f4a2a85fea27c0f8e4d7bbeefb61))
* add authentication setup for VS Code integration ([2284ba7](https://github.com/opencontextprotocol/ocp-spec/commit/2284ba77fca48d9aa5cb493b3f2ebce29db3e3b9))
* add community registry integration for fast API discovery ([438595a](https://github.com/opencontextprotocol/ocp-spec/commit/438595ae249bda7252eca50c08b1f2fe669e1a85))
* add complete Python client library (ocp-agent v0.1.0) ([d838e9a](https://github.com/opencontextprotocol/ocp-spec/commit/d838e9aa7c74b6f9d432053de9e40d1d9a8257d9))
* add Docker workflow for building and pushing images ([d817958](https://github.com/opencontextprotocol/ocp-spec/commit/d8179580f920f9a2bca14903650faac0fc37d662))
* add Dockerfile for multi-stage Hugo build ([72b9d35](https://github.com/opencontextprotocol/ocp-spec/commit/72b9d35d2d0f9da3a4b1987f66bce984404391b5))
* add GitHub Actions workflow for documentation deployment ([45a5ce9](https://github.com/opencontextprotocol/ocp-spec/commit/45a5ce9e4cf73f5f56bd802e9b26d649c051315a))
* add HTTP protocol documentation and tool generation ([5b2bd1f](https://github.com/opencontextprotocol/ocp-spec/commit/5b2bd1f3b1c630576c5f982ab4c83792c51dac2d))
* add icon for OCP VSCode extension ([38a6679](https://github.com/opencontextprotocol/ocp-spec/commit/38a667947b9ac55d1e98a0da4697fa88cfbd16e1))
* add implementation summary for OCP VS Code extension ([f64b648](https://github.com/opencontextprotocol/ocp-spec/commit/f64b64833f068812068a833e65089734ecbf4c6b))
* add learning paths section to documentation ([40051d0](https://github.com/opencontextprotocol/ocp-spec/commit/40051d04dd9856bac3cde4289c9f536561ee2de2))
* add license and esbuild configuration files ([05347cf](https://github.com/opencontextprotocol/ocp-spec/commit/05347cffd606e3475cb94b14f04c30da99500ac3))
* add local storage and caching for OCP agent ([b7ef730](https://github.com/opencontextprotocol/ocp-spec/commit/b7ef730153dbfbf7d6fad0d4aca1589de7fa76c7))
* add local storage and caching for OCP client libraries ([625b40f](https://github.com/opencontextprotocol/ocp-spec/commit/625b40fc74dbdf51e73a73c07b5023e44429eab0))
* add navigation links to schema documentation ([c7e73e2](https://github.com/opencontextprotocol/ocp-spec/commit/c7e73e23d6c4f2e6e2ae7964eff8a7eb81c394a2))
* add OCP CLI implementation with context management and API testing features ([e3478ac](https://github.com/opencontextprotocol/ocp-spec/commit/e3478ac62a11782a8d1e9ff8fc20693dda8521cc))
* add OCP tool schema definition ([4374d89](https://github.com/opencontextprotocol/ocp-spec/commit/4374d892079a90feeed095937fa57caa43b5507f))
* add OCPStorage for API caching and session persistence ([4a78799](https://github.com/opencontextprotocol/ocp-spec/commit/4a78799358783d2f8c5600ae8ba05cd7a30f543f))
* Add Open Context Protocol (OCP) VS Code extension ([8c610c3](https://github.com/opencontextprotocol/ocp-spec/commit/8c610c3ed6de060b1245f3dab64ab6a6094801b5))
* add Python version specification file ([c85c064](https://github.com/opencontextprotocol/ocp-spec/commit/c85c064a4d0c5a2cab6f8940a9fea9ede075058e))
* add README, LICENSE, and .gitignore files ([b18d66c](https://github.com/opencontextprotocol/ocp-spec/commit/b18d66cac719f822b0a11b80336725681d05474c))
* add registry integration and update CLI documentation ([e39bc8f](https://github.com/opencontextprotocol/ocp-spec/commit/e39bc8fda0512e453999b28feb79aa0a15db7d7a))
* add schema ([99abc98](https://github.com/opencontextprotocol/ocp-spec/commit/99abc98bd1b796d0e61ae4d96fe4028e7148614a))
* add schema discovery for complete MCP feature parity ([c7a4e86](https://github.com/opencontextprotocol/ocp-spec/commit/c7a4e8669992e0175b27f1ada2a6645c52d2e2a5))
* add schema documentation generation and update schemas ([386e2dc](https://github.com/opencontextprotocol/ocp-spec/commit/386e2dc907cf1bd391a408a7152b9c6bdf0935cf))
* add storage spec ([91a51b1](https://github.com/opencontextprotocol/ocp-spec/commit/91a51b15dcb5887aec20803a5fda97d8d27af41d))
* add summary and category filtering to registry list ([911c173](https://github.com/opencontextprotocol/ocp-spec/commit/911c173c40d6a68145d0a43168bcc12b1cbc8e0d))
* add Tailwind CSS configuration and styles ([2102697](https://github.com/opencontextprotocol/ocp-spec/commit/21026977c83d36e3dbdcdcb7367f69fbe394a8cf))
* add testing framework and initial test cases ([99543bb](https://github.com/opencontextprotocol/ocp-spec/commit/99543bba32a1618bb4336ce38a7710795509c038))
* add validation tests, TypeScript configuration, and refactor HTTP client ([d6c6c95](https://github.com/opencontextprotocol/ocp-spec/commit/d6c6c9525efa600e3f5680e42f2ced26629a5807))
* add VS Code extension documentation ([da4d077](https://github.com/opencontextprotocol/ocp-spec/commit/da4d07756d783fad06ad7d73e97526f388493653))
* add web app manifest for Open Context Protocol ([1eada4c](https://github.com/opencontextprotocol/ocp-spec/commit/1eada4cb361011de7dffd0213af39e7bbbe337d2))
* Complete OCP Community Registry with pre-discovered tools ([3d94ea1](https://github.com/opencontextprotocol/ocp-spec/commit/3d94ea13411f1aa249cf7bf1cb64bb6a8a2a8597))
* **DOCS-123:** add documentation for OCP features and schemas ([eb53eb8](https://github.com/opencontextprotocol/ocp-spec/commit/eb53eb87c4cb28f6c7dd7b52da0319fc7f422ed3))
* enhance documentation and update dependencies ([89f27d3](https://github.com/opencontextprotocol/ocp-spec/commit/89f27d3df4b56f15ef0778baee66f75db0c01146))
* enhance documentation for OCP setup and usage ([2014c7a](https://github.com/opencontextprotocol/ocp-spec/commit/2014c7a50957fa60bc61d29696338d8b77cfd319))
* enhance documentation for OCP tool discovery ([265012b](https://github.com/opencontextprotocol/ocp-spec/commit/265012bfb3d57989e51f8ecc7988f4a1829cded6))
* enhance OCP agent with Python examples and context management ([96023a2](https://github.com/opencontextprotocol/ocp-spec/commit/96023a2eb062beb5ba7967475aa0c2990f7d10dc))
* enhance OCP CLI documentation and functionality ([1f5ed44](https://github.com/opencontextprotocol/ocp-spec/commit/1f5ed44b442571e3a132eaa30e332cec8fd3b031))
* enhance OCP documentation for clarity and structure ([2caa0af](https://github.com/opencontextprotocol/ocp-spec/commit/2caa0af96e9763737589ad4c1b6f193f7e1ebe48))
* enhance OCPStorage API caching and session handling ([d4be311](https://github.com/opencontextprotocol/ocp-spec/commit/d4be311501a1a807b78e7af2046c50cce96054a9))
* enhance protocol specification and tool generation ([3fd768b](https://github.com/opencontextprotocol/ocp-spec/commit/3fd768b85740702452a4192bec5c6305079f3ca2))
* enhance schema documentation with default values ([d253fc5](https://github.com/opencontextprotocol/ocp-spec/commit/d253fc58f3f5f7159738714defa2e4f68477708c))
* enhance tool descriptions and error handling ([cf68b0f](https://github.com/opencontextprotocol/ocp-spec/commit/cf68b0ffb20080d289f24c4cca86a1a1b417109c))
* generate tools.json files from OpenAPI specs ([c54e9cc](https://github.com/opencontextprotocol/ocp-spec/commit/c54e9cce06df2c42fb660f514405945c669f586f))
* Implement OCP error handling and HTTP client enhancements ([8085778](https://github.com/opencontextprotocol/ocp-spec/commit/808577827ed9e19ac7bc6704b7f632d35de8de27))
* implement OCPStorage class for caching and sessions ([0b3742b](https://github.com/opencontextprotocol/ocp-spec/commit/0b3742bd4fb9841df88c301859a3937881bda494))
* improve API authentication handling in tools ([66149f4](https://github.com/opencontextprotocol/ocp-spec/commit/66149f440a31686003d5ca64ae098a79b76f4b1a))
* improve clarity in tool registration documentation ([052d40d](https://github.com/opencontextprotocol/ocp-spec/commit/052d40d7613b646ad7507b8b18dd70607d234368))
* integrate OCP registry for API discovery and error handling ([8e271f2](https://github.com/opencontextprotocol/ocp-spec/commit/8e271f27789156bf4c6c9ebbdee80c9dfe582f00))
* pivot to hugo ([148d6fb](https://github.com/opencontextprotocol/ocp-spec/commit/148d6fb377a19aac7cf02ae216fcfc4b9c345255))
* push first draft of spec ([5ba6397](https://github.com/opencontextprotocol/ocp-spec/commit/5ba6397f87d41fb8d3b9c2b61b990eb437c841ce))
* refine context schema documentation and remove callouts ([e30b36d](https://github.com/opencontextprotocol/ocp-spec/commit/e30b36d92d4592d948936d7dee638b65a8352181))
* refine OCP overview and compatibility levels ([0c684b1](https://github.com/opencontextprotocol/ocp-spec/commit/0c684b197e3907ab66138a9ce35689e9699da0f9))
* remove agent context documentation and code of conduct ([eae979c](https://github.com/opencontextprotocol/ocp-spec/commit/eae979cb0494e6019c7d4a94c38a1169a53e6a50))
* remove GitHub and Stripe API examples ([e91254a](https://github.com/opencontextprotocol/ocp-spec/commit/e91254af9f5c990c691c4268eaeaf92811a30ca1))
* remove outdated guides and documentation ([ce8971e](https://github.com/opencontextprotocol/ocp-spec/commit/ce8971e54cae0b74abf9053bd99555c552aae148))
* remove redundant section from specification ([6e13d97](https://github.com/opencontextprotocol/ocp-spec/commit/6e13d9731d6e919c3c8dcace705c4f50efb2e7b8))
* remove unused icon file from OCP VSCode extension ([5feeb3a](https://github.com/opencontextprotocol/ocp-spec/commit/5feeb3abc47d937e46ec9222a6477d9fe0fb7c91))
* rename OCP_GOAL to OCP_AGENT_GOAL and add OCP_USER ([5936690](https://github.com/opencontextprotocol/ocp-spec/commit/593669004c428640f18ac25cf09583fa1b778cf0))
* rename OCP-Agent-Goal to OCP-Current-Goal ([aabd87d](https://github.com/opencontextprotocol/ocp-spec/commit/aabd87d78e502d110f3915e12479dd3c8a128e1c))
* rename OpenAPI Extensions Schema to OpenAPI Schema ([d133dc8](https://github.com/opencontextprotocol/ocp-spec/commit/d133dc8ab3a4c90938bf8cc5392728fe860219a7))
* rename site folder to docs ([2ca8653](https://github.com/opencontextprotocol/ocp-spec/commit/2ca8653e106082082da4ede1c3eb5e9d573e578a))
* reorganize roadmap for clarity and structure ([a3c707e](https://github.com/opencontextprotocol/ocp-spec/commit/a3c707ee5c7170ae3f131982bb5cb1cae9eec83b))
* replace favicon.ico with favicon.svg and remove webmanifest ([6aaaf30](https://github.com/opencontextprotocol/ocp-spec/commit/6aaaf30b258db5734fe2c59ae1f79cc29d3d4f4f))
* restructure documentation and add installation guide ([ab10fca](https://github.com/opencontextprotocol/ocp-spec/commit/ab10fcaceaf0cc9a32b6121e54c30e0556194a69))
* restructure specification for clarity and detail ([2813925](https://github.com/opencontextprotocol/ocp-spec/commit/2813925429af58b239fe98f225a56c512f916c15))
* simplify caching mechanism and enhance tool documentation ([7dd94f0](https://github.com/opencontextprotocol/ocp-spec/commit/7dd94f03f5dd2a2203f193111a65d201924497ff))
* update API authentication to use headers ([f4cbc5b](https://github.com/opencontextprotocol/ocp-spec/commit/f4cbc5b8a046c5a13ebe3bf5f4e386b4a595708a))
* update card icons for improved clarity ([8ab02bf](https://github.com/opencontextprotocol/ocp-spec/commit/8ab02bf479345c4342c586000ce9390a112528ec))
* update cards for consistency and clarity across documentation ([246204d](https://github.com/opencontextprotocol/ocp-spec/commit/246204d5b4bc43106c37748fb729ef96bac361e9))
* update context and roadmap for JavaScript library ([9a738c6](https://github.com/opencontextprotocol/ocp-spec/commit/9a738c63e63b50d77e1ea94d0c7be0e083dd2a0e))
* update documentation and remove obsolete context file ([7280608](https://github.com/opencontextprotocol/ocp-spec/commit/7280608b7209e8109e7aca9623acb470f1cf14cd))
* update documentation and remove obsolete files ([322f81e](https://github.com/opencontextprotocol/ocp-spec/commit/322f81e33f2523fe3d5c7fa9cbeb64eb40944e20))
* update documentation for clarity and consistency ([92adf03](https://github.com/opencontextprotocol/ocp-spec/commit/92adf031d3a06bb3687c71b14d13a829b2095702))
* update documentation for clarity and organization ([a8d72e5](https://github.com/opencontextprotocol/ocp-spec/commit/a8d72e531c225069d31c8d82d5f520a88caa6d19))
* update documentation for consistency and clarity ([86be5b0](https://github.com/opencontextprotocol/ocp-spec/commit/86be5b0d0a03d1660683f2b7257018f9b3eb5ebf))
* update documentation links and remove obsolete files ([08f018a](https://github.com/opencontextprotocol/ocp-spec/commit/08f018adec256ac6295922437307df107d1ccae2))
* update documentation weights and add learning paths ([cd9b4a7](https://github.com/opencontextprotocol/ocp-spec/commit/cd9b4a7400f762ce66f25730fd316fd1eaa8114f))
* update feature cards for consistency and clarity ([4d4dda5](https://github.com/opencontextprotocol/ocp-spec/commit/4d4dda5782cd0afb93cfd754da223baf1e630b7e))
* update feature cards with links for clarity ([04a1985](https://github.com/opencontextprotocol/ocp-spec/commit/04a198517f0473399d424e83245fa5595f1b884d))
* update file extensions from .py to .js in tests ([b5c45d6](https://github.com/opencontextprotocol/ocp-spec/commit/b5c45d6f4012db2e0a000709dd3097f8e293ef2e))
* update GitHub and Stripe examples for clarity ([3fec2e9](https://github.com/opencontextprotocol/ocp-spec/commit/3fec2e9b332c8e0351873bb03a94d061120b0acc))
* update GitHub token usage in quick start examples ([f272a9f](https://github.com/opencontextprotocol/ocp-spec/commit/f272a9ffd8accc839bad9bc8efc2c3065ae92e12))
* update hero section for clarity and consistency ([3a741a6](https://github.com/opencontextprotocol/ocp-spec/commit/3a741a6185c99bb33184e33c90e1f58ef2471e02))
* update interaction logging to use api_call prefix ([73b4834](https://github.com/opencontextprotocol/ocp-spec/commit/73b4834a9790f8ba488e0377452ddab21e09829e))
* update model selection to use user-selected chat model ([6bc10d4](https://github.com/opencontextprotocol/ocp-spec/commit/6bc10d431268a7e942fc7c6dcd35ecbcbf54170b))
* update navigation links in documentation ([56cb9e7](https://github.com/opencontextprotocol/ocp-spec/commit/56cb9e7f9a01c86d0e8e1ff08df6af571e446259))
* update OCP schemas for enhanced context support ([7202e45](https://github.com/opencontextprotocol/ocp-spec/commit/7202e451e0a50242092346886f41ddea3b9c940c))
* update package names to use [@opencontextprotocol](https://github.com/opencontextprotocol) ([664e1b3](https://github.com/opencontextprotocol/ocp-spec/commit/664e1b3a042b296c57a786389f634d15685d8e1d))
* update poetry.lock and pyproject.toml for dev dependencies ([f783101](https://github.com/opencontextprotocol/ocp-spec/commit/f783101c3f0c78dd26d4b3a10667c63ac0eefd15))
* update README to clarify OCP benefits and usage ([e0a7027](https://github.com/opencontextprotocol/ocp-spec/commit/e0a702744e9cd295f83bf44ad952af0359dc037e))
* update roadmap for clarity and structure ([b62a164](https://github.com/opencontextprotocol/ocp-spec/commit/b62a164d8aee16d70d1f69bb4c62b25a27ad2dd8))
* update schema files and validation logic ([31d3257](https://github.com/opencontextprotocol/ocp-spec/commit/31d3257364faab7aad66e8f7da2142346b2dff52))
* update specification for context-aware API integration ([5b849cf](https://github.com/opencontextprotocol/ocp-spec/commit/5b849cfbb6f91fa2b80dc1f142a9ad56d6ec5aea))
* update title for Open Context Protocol v1.0 ([7a51f0b](https://github.com/opencontextprotocol/ocp-spec/commit/7a51f0b8cf0f16d37920afe7744839df5887df45))
* update tool discovery documentation for clarity ([b849d9c](https://github.com/opencontextprotocol/ocp-spec/commit/b849d9cc97ee063819c56509bc8c75f753dabcaa))
* **vscode:** implement OCP vs MCP demonstration extension ([b4ef0ad](https://github.com/opencontextprotocol/ocp-spec/commit/b4ef0adc42c7823ce53aa0fc685ea58cd04adbfb))


### Bug Fixes

* add generated registry content to .gitignore ([c9bc2bc](https://github.com/opencontextprotocol/ocp-spec/commit/c9bc2bc824b20b9d7f36485686b5eac9dffd1066))
* add POETRY_SYSTEM_GIT_CLIENT environment variable ([9faa2f0](https://github.com/opencontextprotocol/ocp-spec/commit/9faa2f0e56a9b94c466df05137fedc5cb049688d))
* clarify IDE integration documentation ([52f1e82](https://github.com/opencontextprotocol/ocp-spec/commit/52f1e82d840bdc7e802917a911a7616ddb4c45a5))
* clarify library names in README.md ([9d71b0b](https://github.com/opencontextprotocol/ocp-spec/commit/9d71b0b58a6bdcb766ba4aa675281fc5a9d1cd74))
* correct formatting in README.md ([3800e00](https://github.com/opencontextprotocol/ocp-spec/commit/3800e005f72054fb3649e85462936d8ee2625234))
* correct links for Open Standards and Compatibility sections ([0b492d6](https://github.com/opencontextprotocol/ocp-spec/commit/0b492d6c27d4099c844bc70e01e5831fae147003))
* correct logo width in hugo configuration ([47c60e4](https://github.com/opencontextprotocol/ocp-spec/commit/47c60e43de5e103749cca2447cecdb6b7e83b685))
* correct typo in linkTitle in _index.md ([ca66d17](https://github.com/opencontextprotocol/ocp-spec/commit/ca66d17d82c68a5b406afb102e0780f706ead14d))
* enhance protocol overview and header specifications ([568c263](https://github.com/opencontextprotocol/ocp-spec/commit/568c263eff78ec344765498d94fe682d0401cab5))
* enhance tool discovery documentation for clarity ([0f04ea6](https://github.com/opencontextprotocol/ocp-spec/commit/0f04ea66957de37f617070effe9f33d343d028f7))
* improve error messages for RegistryUnavailable ([f867284](https://github.com/opencontextprotocol/ocp-spec/commit/f8672847bc5610385afd3c984244339d3526916b))
* improve VS Code extension documentation clarity ([396ca43](https://github.com/opencontextprotocol/ocp-spec/commit/396ca439d57cb253a3578bec7ea555812b7a4951))
* refine tool discovery documentation for clarity ([552b16c](https://github.com/opencontextprotocol/ocp-spec/commit/552b16c3fff23ba0f69bdf04d9d0b9648d6f91e2))
* remove CLI Tool link from implementation libraries ([4bcad98](https://github.com/opencontextprotocol/ocp-spec/commit/4bcad98f8cf3f877ddfb8c8ae4e3798bd88813b8))
* remove Learning Paths from navigation menu ([6f22e1b](https://github.com/opencontextprotocol/ocp-spec/commit/6f22e1bc252058aaf06d8905b96bc41d1f07e004))
* remove obsolete GitHub Pages workflow ([d207db9](https://github.com/opencontextprotocol/ocp-spec/commit/d207db9b9d3fbabbd596c304f36b9196330dac1d))
* remove OCP HTTP Interceptor and related test files ([b379d02](https://github.com/opencontextprotocol/ocp-spec/commit/b379d025445a4652d561dc439a82294a94462760))
* remove unnecessary code blocks in specification ([5d1a5af](https://github.com/opencontextprotocol/ocp-spec/commit/5d1a5af59c951de7c8697db6ed8eee1e73cafa8e))
* remove unnecessary pytest configuration ([54f68b1](https://github.com/opencontextprotocol/ocp-spec/commit/54f68b12b2ceb66d47aeb47cbb87161519cae5d3))
* rename package from ocp-agent to open-context-agent ([5e6bf3f](https://github.com/opencontextprotocol/ocp-spec/commit/5e6bf3fc2c0a4e1b510707ae85e01434422bdd35))
* revert version to 0.1.0 in pyproject.toml ([3de5cb3](https://github.com/opencontextprotocol/ocp-spec/commit/3de5cb3110753105734a34ee8f82cae8d18766bd))
* simplify registry content generation command ([f1016e5](https://github.com/opencontextprotocol/ocp-spec/commit/f1016e5aac137ce4301a6987487f101984b66fda))
* trigger deployment to VPS after Docker build ([e45521a](https://github.com/opencontextprotocol/ocp-spec/commit/e45521ac7f20e0cd9ff8fb2420c76d36cf1e35a2))
* update artifact path for documentation deployment ([fc053d7](https://github.com/opencontextprotocol/ocp-spec/commit/fc053d7c6c8e701f743ccb0d16d682c9de98513b))
* update author name to OCP Contributors ([f84027e](https://github.com/opencontextprotocol/ocp-spec/commit/f84027e5f28c35df0de003180731110c4d16259f))
* update default registry URL in documentation ([ff2fc96](https://github.com/opencontextprotocol/ocp-spec/commit/ff2fc96de553b8c477d64f8fc4ff7660ea6f377c))
* update default registry URLs in documentation ([797f638](https://github.com/opencontextprotocol/ocp-spec/commit/797f63860f33bd2b5dace8ac19871e6b5ffdc829))
* update description in pyproject.toml ([dc50566](https://github.com/opencontextprotocol/ocp-spec/commit/dc505668573ce7563829b541bb6ea66cb102b0bb))
* update development server setup and build process ([a85ecef](https://github.com/opencontextprotocol/ocp-spec/commit/a85ecef321ba45a0fb8d5c70ae69125941f339b3))
* update Docker build context to current directory ([0880473](https://github.com/opencontextprotocol/ocp-spec/commit/088047328808db9028192d9d95ce8299f5ef213b))
* update Dockerfile to mount SSH for venv creation ([991a640](https://github.com/opencontextprotocol/ocp-spec/commit/991a64033283c4274c1c2b10e4bc3d6b1d1ed402))
* update emoji icons in README for clarity ([f1b8c37](https://github.com/opencontextprotocol/ocp-spec/commit/f1b8c377d7f2de7768f07198d8fa223786c903cc))
* update examples to use generic OCP approach after removing convenience functions ([d20d73b](https://github.com/opencontextprotocol/ocp-spec/commit/d20d73b67d2348f4c334b89dd98cc6cb03dc472c))
* update feature card titles for consistency ([ebf7c82](https://github.com/opencontextprotocol/ocp-spec/commit/ebf7c82179b8dbace979bd3082a05efd99e3c21c))
* update getting started guide for clarity and examples ([87c6c31](https://github.com/opencontextprotocol/ocp-spec/commit/87c6c310c6a3c596e67e6591ec5b7658bc78597f))
* update import paths to ocp_agent module ([58f4584](https://github.com/opencontextprotocol/ocp-spec/commit/58f458492ed7133fe76c80b0a4be958c3de1b89c))
* update JSON Schema links for consistency ([b1ba770](https://github.com/opencontextprotocol/ocp-spec/commit/b1ba770eb3e1bd245928088f1e7be0516d0fe820))
* update menu weights and add Registry link ([bb1c1bb](https://github.com/opencontextprotocol/ocp-spec/commit/bb1c1bb6a8ac691630ffa95bcbe9437cf12f35f1))
* update navigation links for IDE and Registry Client ([5522167](https://github.com/opencontextprotocol/ocp-spec/commit/55221677bad85a621a8c66f73240536faa244e98))
* update ocp-badge-name styles for consistency ([43f7d7b](https://github.com/opencontextprotocol/ocp-spec/commit/43f7d7b6b9bdc18bf3e66166c567dcac08c88535))
* update ocp-registry dependency installation method ([2604787](https://github.com/opencontextprotocol/ocp-spec/commit/2604787cb7bc5256be1b7e5ea85ff320d7d0ae34))
* update ocp-registry dependency installation method ([cb19fe0](https://github.com/opencontextprotocol/ocp-spec/commit/cb19fe0d94c9c16ee02b900b445273931b038392))
* update ocp-registry dependency installation method ([f2a5adf](https://github.com/opencontextprotocol/ocp-spec/commit/f2a5adf62de69972d6b3239db5c0bfe1ada6ddaa))
* update PATH to include Poetry's venv ([9415993](https://github.com/opencontextprotocol/ocp-spec/commit/9415993c55b41e35fbcf79015d02bffac8fcf46e))
* update paths in Makefile and hugo.yaml for consistency ([767ccb9](https://github.com/opencontextprotocol/ocp-spec/commit/767ccb9fc88900b3023b15c5dac547e4ee19c284))
* update README for consistent formatting ([b3ea4cf](https://github.com/opencontextprotocol/ocp-spec/commit/b3ea4cf1fcccaf1bb68485d707f0a45a26c361ab))
* update section title for clarity in tool discovery ([8495842](https://github.com/opencontextprotocol/ocp-spec/commit/8495842be848546edf9b5a7ad96988c673c4c556))
* update tool naming rules to use camelCase normalization ([3b7a3db](https://github.com/opencontextprotocol/ocp-spec/commit/3b7a3dbd1fd69ddb9b58f9b15afe6beef001fe6d))


### Code Refactoring

* clean up OCP implementation and remove MCP references ([fa7e792](https://github.com/opencontextprotocol/ocp-spec/commit/fa7e79200bf8811fc293d140044d2a2b6bf7d4f1))
* **python:** remove hardcoded API integrations ([9f29d2f](https://github.com/opencontextprotocol/ocp-spec/commit/9f29d2fffe347aeb51b872d5c8bc7c23eb1d684c))

