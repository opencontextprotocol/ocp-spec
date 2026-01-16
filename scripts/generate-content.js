#!/usr/bin/env node

/**
 * Generate Hugo content from OCP Registry data.
 * 
 * Fetches API definitions from GitHub and renders Jinja2-compatible templates
 * using Nunjucks to generate Hugo markdown pages.
 */

const { writeFile, mkdir } = require('fs/promises');
const { join } = require('path');
const yaml = require('js-yaml');
const nunjucks = require('nunjucks');

// Configuration
const OUTPUT_DIR = join(__dirname, '..', 'docs', 'content', 'registry');
const TEMPLATE_DIR = join(__dirname, 'templates');
const REGISTRY_REPO = 'opencontextprotocol/ocp-registry';
const REGISTRY_REF = 'main';

/**
 * Get relative path from project root
 */
function getRelativePath(absolutePath) {
  const projectRoot = join(__dirname, '..');
  return absolutePath.replace(projectRoot + '/', '');
}

/**
 * Fetch a file from GitHub raw content
 */
async function fetchGitHubFile(repo, ref, path) {
  const url = `https://raw.githubusercontent.com/${repo}/${ref}/${path}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      if (response.status === 404) return null;
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.text();
  } catch (error) {
    console.error(`⚠️  Error fetching ${path}: ${error.message}`);
    return null;
  }
}

/**
 * List all API directories in the registry
 */
async function listRegistryApis(repo, ref) {
  const url = `https://api.github.com/repos/${repo}/contents/data/apis?ref=${ref}`;
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data
      .filter(item => item.type === 'dir')
      .map(item => item.name);
  } catch (error) {
    console.error(`❌ Error listing APIs from registry: ${error.message}`);
    return [];
  }
}

/**
 * Load API metadata from GitHub
 */
async function loadApiMeta(repo, ref, apiName) {
  const content = await fetchGitHubFile(repo, ref, `data/apis/${apiName}/meta.yaml`);
  if (!content) {
    console.log(`Warning: No meta.yaml found for ${apiName}`);
    return null;
  }
  
  try {
    return yaml.load(content);
  } catch (error) {
    console.error(`❌ Error parsing meta.yaml for ${apiName}: ${error.message}`);
    return null;
  }
}

/**
 * Load tools from GitHub
 */
async function loadApiTools(repo, ref, apiName) {
  const content = await fetchGitHubFile(repo, ref, `data/apis/${apiName}/tools.json`);
  if (!content) {
    console.log(`Warning: No tools.json found for ${apiName}`);
    return { version: null, tools: [] };
  }
  
  try {
    const data = JSON.parse(content);
    
    if (data && typeof data === 'object' && Array.isArray(data.tools)) {
      return { version: data.version || null, tools: data.tools };
    } else {
      console.error(`❌ Invalid tools.json format for ${apiName}. Expected {version, tools}.`);
      return { version: null, tools: [] };
    }
  } catch (error) {
    console.error(`❌ Error parsing tools.json for ${apiName}: ${error.message}`);
    return { version: null, tools: [] };
  }
}

/**
 * Setup Nunjucks environment
 */
function setupNunjucks(templateDir) {
  const env = new nunjucks.Environment(
    new nunjucks.FileSystemLoader(templateDir),
    {
      autoescape: false,
      trimBlocks: true,
      lstripBlocks: true
    }
  );
  
  // Add custom filters
  env.addFilter('toyaml', (data) => {
    return yaml.dump(data, { lineWidth: -1 }).trim();
  });
  
  env.addFilter('tojson', (data) => {
    return JSON.stringify(data, null, 2);
  });
  
  // Group by filter (like Jinja2's groupby)
  env.addFilter('groupby', (items, attr) => {
    const groups = {};
    items.forEach(item => {
      const key = item[attr] || 'general';
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    });
    return Object.entries(groups);
  });
  
  env.addFilter('dictsort', (dict) => {
    return Object.entries(dict).sort((a, b) => a[0].localeCompare(b[0]));
  });
  
  env.addFilter('resource_name', (name) => {
    const segments = String(name).split('.');
    return segments[segments.length - 1];
  });
  
  return env;
}

/**
 * Generate main API page
 */
async function generateApiPage(env, meta, apiVersion, tools, outputDir) {
  try {
    const apiOutputDir = join(outputDir, 'catalog', meta.name);
    await mkdir(apiOutputDir, { recursive: true });
    
    // Prepare authentication data
    const authConfig = meta.auth_config || {};
    const apiAuthentication = {
      type: (authConfig.type || 'bearer_token').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
      documentation: authConfig.instructions || 'See documentation for authentication details.'
    };
    
    // Generate frontmatter
    const frontmatter = {
      title: meta.display_name,
      description: meta.description,
      weight: 10,
      type: 'docs',
      params: {
        api_name: meta.name,
        api_version: apiVersion,
        base_url: meta.base_url || '',
        category: meta.category,
        tags: meta.tags || [],
        tool_count: tools.length,
        openapi_url: meta.openapi_url,
        documentation_url: meta.documentation_url || '',
        rate_limit: meta.rate_limit || '',
        status: meta.status || 'active',
        auth_config: authConfig,
        contact: meta.contact || {}
      }
    };
    
    // Prepare context
    const context = {
      frontmatter,
      api: {
        name: meta.name,
        display_name: meta.display_name,
        description: meta.description,
        category: meta.category,
        base_url: meta.base_url || '',
        documentation_url: meta.documentation_url,
        authentication: apiAuthentication
      },
      api_version: apiVersion,
      tools,
      tool_count: tools.length
    };
    
    // Render template
    const content = env.render('api-page.md.j2', context);
    
    // Write content
    const outputFile = join(apiOutputDir, '_index.md');
    await writeFile(outputFile, content, 'utf8');
    console.log(`✓ Generated ${getRelativePath(outputFile)}`);
    return true;
  } catch (error) {
    console.error(`❌ Error generating API page for ${meta.name}: ${error.message}`);
    console.error(error.stack);
    return false;
  }
}

/**
 * Generate individual tool pages
 */
async function generateToolPages(env, meta, tools, outputDir) {
  if (!tools || tools.length === 0) return 0;
  
  let count = 0;
  
  for (const tool of tools) {
    try {
      const toolsDir = join(outputDir, 'catalog', meta.name, 'tools');
      await mkdir(toolsDir, { recursive: true });
      
      // Generate frontmatter
      const frontmatter = {
        title: tool.name,
        description: tool.description || '',
        weight: 20,
        type: 'docs',
        sidebar: { exclude: true },
        params: {
          tool_name: tool.name,
          api_name: meta.name,
          method: tool.method || 'GET',
          path: tool.path || '',
          operation_id: tool.operation_id || '',
          tags: tool.tags || [],
          resource: tool.resource || 'general'
        }
      };
      
      // Prepare context
      const context = {
        frontmatter,
        tool,
        api_name: meta.name
      };
      
      // Render template
      const content = env.render('tool-page.md.j2', context);
      
      // Write content
      const toolFilename = tool.name.replace(/[_\s]/g, '-').toLowerCase();
      const outputFile = join(toolsDir, `${toolFilename}.md`);
      await writeFile(outputFile, content, 'utf8');
      count++;
    } catch (error) {
      console.error(`❌ Error generating tool page for ${tool.name}: ${error.message}`);
      continue;
    }
  }
  
  if (count > 0) {
    console.log(`✓ Generated ${count} tool pages for ${meta.display_name}`);
  }
  
  return count;
}

/**
 * Generate registry index page
 */
async function generateRegistryIndex(env, apiCount, outputDir) {
  try {
    const frontmatter = {
      title: 'Registry',
      description: 'Pre-configured API integrations for OCP agents',
      weight: 1,
      type: 'docs',
      sidebar: { exclude: true }
    };
    
    const context = { frontmatter, api_count: apiCount };
    const content = env.render('registry-index.md.j2', context);
    
    const outputFile = join(outputDir, '_index.md');
    await writeFile(outputFile, content, 'utf8');
    console.log(`✓ Generated ${getRelativePath(outputFile)}`);
    return true;
  } catch (error) {
    console.error(`❌ Error generating registry index: ${error.message}`);
    return false;
  }
}

/**
 * Generate catalog page
 */
async function generateCatalogPage(env, apisByCategory, outputDir) {
  try {
    const catalogDir = join(outputDir, 'catalog');
    await mkdir(catalogDir, { recursive: true });
    
    const frontmatter = {
      title: 'Browse APIs',
      description: 'Explore all APIs available in the OCP Registry',
      weight: 10,
      type: 'docs'
    };
    
    const context = {
      frontmatter,
      categories: apisByCategory
    };
    
    const content = env.render('catalog.md.j2', context);
    
    const outputFile = join(catalogDir, '_index.md');
    await writeFile(outputFile, content, 'utf8');
    console.log(`✓ Generated ${getRelativePath(outputFile)}`);
    return true;
  } catch (error) {
    console.error(`❌ Error generating catalog page: ${error.message}`);
    return false;
  }
}

/**
 * Generate authentication page
 */
async function generateAuthenticationPage(env, outputDir) {
  try {
    const authDir = join(outputDir, 'authentication');
    await mkdir(authDir, { recursive: true });
    
    const frontmatter = {
      title: 'Authentication',
      description: 'Learn how to configure authentication for OCP Registry APIs',
      weight: 10,
      type: 'docs'
    };
    
    const context = { frontmatter };
    const content = env.render('authentication.md.j2', context);
    
    const outputFile = join(authDir, '_index.md');
    await writeFile(outputFile, content, 'utf8');
    console.log(`✓ Generated ${getRelativePath(outputFile)}`);
    return true;
  } catch (error) {
    console.error(`❌ Error generating authentication page: ${error.message}`);
    return false;
  }
}

/**
 * Main function
 */
async function main() {
  await mkdir(OUTPUT_DIR, { recursive: true });
  
  const env = setupNunjucks(TEMPLATE_DIR);
  
  console.log(`Registry source: ${REGISTRY_REPO}@${REGISTRY_REF}`);
  console.log(`Output directory: ${getRelativePath(OUTPUT_DIR)}`);
  console.log();
  
  // List all APIs from registry
  console.log('Fetching API list from registry...');
  const apiNames = await listRegistryApis(REGISTRY_REPO, REGISTRY_REF);
  
  if (apiNames.length === 0) {
    console.error('Error: No APIs found in registry');
    process.exit(1);
  }
  
  console.log(`Found ${apiNames.length} APIs: ${apiNames.join(', ')}`);
  console.log();
  
  // Process all APIs
  const apis = [];
  let totalTools = 0;
  const apisByCategory = {};
  
  for (const apiName of apiNames.sort()) {
    console.log(`Processing ${apiName}...`);
    
    // Load metadata
    const meta = await loadApiMeta(REGISTRY_REPO, REGISTRY_REF, apiName);
    if (!meta) continue;
    
    // Load tools
    const { version: apiVersion, tools } = await loadApiTools(REGISTRY_REPO, REGISTRY_REF, apiName);
    
    // Generate API page
    if (!await generateApiPage(env, meta, apiVersion, tools, OUTPUT_DIR)) {
      continue;
    }
    
    // Generate tool pages
    const toolCount = await generateToolPages(env, meta, tools, OUTPUT_DIR);
    totalTools += toolCount;
    
    // Track for catalog
    const category = meta.category || 'Other';
    if (!apisByCategory[category]) {
      apisByCategory[category] = [];
    }
    
    apisByCategory[category].push({
      name: meta.name,
      display_name: meta.display_name,
      description: meta.description,
      icon: meta.icon || 'globe',
      tool_count: tools.length
    });
    
    apis.push(meta);
    console.log();
  }
  
  // Generate index pages
  console.log('Generating index pages...');
  await generateRegistryIndex(env, apis.length, OUTPUT_DIR);
  await generateCatalogPage(env, apisByCategory, OUTPUT_DIR);
  await generateAuthenticationPage(env, OUTPUT_DIR);
  
  // Summary
  console.log();
  console.log('Content generation complete!');
  console.log(`  APIs processed: ${apis.length}`);
  console.log(`  Total tools: ${totalTools}`);
  console.log(`  Categories: ${Object.keys(apisByCategory).length}`);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
