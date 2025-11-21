#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Configuration
const SCHEMAS_DIR = path.join(__dirname, '..', 'schemas');
const OUTPUT_DIR = path.join(__dirname, 'content', 'docs', 'specs');

// Schema file mappings
const SCHEMA_CONFIGS = [
  {
    file: 'ocp-context.json',
    outputFile: 'context-schema.md',
    title: 'Context Schema',
    weight: 1,
    description: 'Schema for OCP context objects carried in the OCP-Session header.'
  },
  {
    file: 'ocp-tool.json',
    outputFile: 'tool-schema.md', 
    title: 'Tool Schema',
    weight: 2,
    description: 'Schema for tools generated from OpenAPI specifications.'
  },
  {
    file: 'ocp-openapi-extensions.json',
    outputFile: 'openapi-extensions-schema.md',
    title: 'OpenAPI Schema',
    weight: 3,
    description: 'Schema for OCP extensions in OpenAPI specifications.'
  }
];

function parseProperty(name, prop, required = []) {
  const isRequired = required.includes(name);
  
  // Clean up type display
  let type = prop.type;
  if (Array.isArray(type)) {
    // Handle ["string", "null"] -> "string?"
    if (type.includes("null")) {
      const mainType = type.find(t => t !== "null");
      type = mainType ? `${mainType}?` : "any";
    } else {
      type = type.join(" | ");
    }
  } else if (!type) {
    type = "any";
  }

  // Check if property has constraints that warrant a dedicated section
  const hasConstraints = prop.enum || prop.pattern || prop.format || 
                        prop.minLength || prop.maxLength || 
                        prop.minimum !== undefined || prop.maximum !== undefined ||
                        prop.default !== undefined;

  // Add links for complex types that will have their own sections
  const hasNestedContent = (prop.type === 'object' && (prop.properties || prop.patternProperties)) || 
                           (prop.type === 'array' && prop.items && prop.items.properties) ||
                           hasConstraints;
  
  if (hasNestedContent) {
    type = `[${type}](#${name.toLowerCase()})`;
  }
  
  const description = prop.description || '*No description provided*';
  
  return {
    name,
    type,
    required: isRequired ? 'Yes' : 'No',
    description: description,
    hasConstraints: hasConstraints
  };
}

function generateNavigation(weight) {
  // Read the parent spec page weight dynamically
  const specIndexPath = path.join(OUTPUT_DIR, '_index.md');
  
  if (!fs.existsSync(specIndexPath)) {
    throw new Error(`Spec index file not found at ${specIndexPath}`);
  }
  
  const specContent = fs.readFileSync(specIndexPath, 'utf8');
  const specWeightMatch = specContent.match(/weight:\s*(\d+)/);
  
  if (!specWeightMatch) {
    throw new Error(`Weight not found in spec index file at ${specIndexPath}. Weight must be set in frontmatter.`);
  }
  
  const specWeight = parseInt(specWeightMatch[1]);
  
  // Find the next section after spec by scanning all docs pages
  const docsDir = path.join(__dirname, 'content', 'docs');
  const docsSections = fs.readdirSync(docsDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => {
      const indexPath = path.join(docsDir, dirent.name, '_index.md');
      if (fs.existsSync(indexPath)) {
        const content = fs.readFileSync(indexPath, 'utf8');
        const weightMatch = content.match(/weight:\s*(\d+)/);
        return {
          name: dirent.name,
          weight: weightMatch ? parseInt(weightMatch[1]) : 999
        };
      }
      return null;
    })
    .filter(Boolean)
    .sort((a, b) => a.weight - b.weight);
  
  const nextSectionAfterSpec = docsSections.find(section => section.weight > specWeight);
  
  // Sort schema configs by weight to find prev/next
  const sortedConfigs = SCHEMA_CONFIGS.sort((a, b) => a.weight - b.weight);
  const currentIndex = sortedConfigs.findIndex(config => config.weight === weight);
  
  let navigation = '';
  
  // Previous page
  if (weight === 1) {
    // First page: prev is always the parent spec page
    navigation += '\nprev: /docs/specs/';
  } else {
    // Find previous page by weight
    const prevConfig = sortedConfigs[currentIndex - 1];
    if (prevConfig) {
      const prevSlug = prevConfig.outputFile.replace('.md', '/');
      navigation += `\nprev: /docs/specs/${prevSlug}`;
    }
  }
  
  // Next page
  if (currentIndex === sortedConfigs.length - 1) {
    // Last page: next is the section after spec
    if (nextSectionAfterSpec) {
      navigation += `\nnext: /docs/${nextSectionAfterSpec.name}/`;
    }
  } else {
    // Find next page by weight
    const nextConfig = sortedConfigs[currentIndex + 1];
    if (nextConfig) {
      const nextSlug = nextConfig.outputFile.replace('.md', '/');
      navigation += `\nnext: /docs/specs/${nextSlug}`;
    }
  }
  
  return navigation;
}

function generateSchemaMarkdown(config) {
  const schemaPath = path.join(SCHEMAS_DIR, config.file);
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  
  // Generate next/prev navigation based on weight
  const navigation = generateNavigation(config.weight);
  
  let markdown = `---
title: ${config.title}
weight: ${config.weight}${navigation}
cascade:
  type: docs
---

${config.description}

**JSON Schema**: [\`/schemas/${config.file}\`](https://github.com/opencontextprotocol/specification/blob/main/schemas/${config.file})

`;

  // Handle schemas with direct properties vs definitions
  if (schema.properties || schema.patternProperties) {
    // Direct properties schema (like ocp-context.json, ocp-tool.json)
    if (schema.properties) {
      markdown += generatePropertiesTable(schema.properties, schema.required || []);
    }
    
    // Add nested objects, arrays, and pattern properties
    markdown += generateNestedStructures(schema);
  } else if (schema.definitions) {
    // Schema with definitions (like ocp-openapi-extensions.json)
    markdown += "## Definitions\n\n";
    
    for (const [defName, defSchema] of Object.entries(schema.definitions)) {
      markdown += `### \`${defName}\`\n\n`;
      if (defSchema.description) {
        markdown += `${defSchema.description}\n\n`;
      }
      
      if (defSchema.properties) {
        markdown += generatePropertiesTable(defSchema.properties, defSchema.required || [], '####');
        markdown += generateNestedStructures(defSchema, defName);
      }
      markdown += "\n";
    }
  } else {
    markdown += "*No properties defined in this schema.*\n";
  }

  return markdown;
}

function generatePropertiesTable(properties, required, headerLevel = '##') {
  let table = `${headerLevel} Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
`;

  // Sort properties: required first, then alphabetical
  const sortedProps = Object.keys(properties).sort((a, b) => {
    const aReq = required.includes(a);
    const bReq = required.includes(b);
    if (aReq && !bReq) return -1;
    if (!aReq && bReq) return 1;
    return a.localeCompare(b);
  });

  for (const propName of sortedProps) {
    const prop = parseProperty(propName, properties[propName], required);
    table += `| \`${prop.name}\` | ${prop.type} | ${prop.required} | ${prop.description} |\n`;
  }

  return table + "\n";
}

function generateNestedStructures(schema, prefix = '') {
  let sections = '';
  
  // Handle regular properties
  if (schema.properties) {
    for (const [propName, propSchema] of Object.entries(schema.properties)) {
      if (propSchema.type === 'object' && (propSchema.properties || propSchema.patternProperties)) {
        sections += generateObjectSection(propName, propSchema, prefix);
      } else if (propSchema.type === 'array' && propSchema.items && propSchema.items.properties) {
        sections += generateArraySection(propName, propSchema, prefix);
      } else if (hasPropertyConstraints(propSchema)) {
        sections += generateConstrainedPropertySection(propName, propSchema, prefix);
      }
    }
  }
  
  // Handle patternProperties - this is the key missing piece!
  if (schema.patternProperties) {
    for (const [pattern, propSchema] of Object.entries(schema.patternProperties)) {
      // Use a friendlier name for the section based on the pattern
      let sectionName = pattern;
      if (pattern === '^[a-zA-Z0-9_-]+$') {
        sectionName = 'parameters'; // Common case for tool parameters
      } else if (pattern === '^[a-zA-Z][a-zA-Z0-9_]*$') {
        sectionName = 'parameters'; // Tool parameter pattern
      } else if (pattern === '^x-') {
        sectionName = 'extensions';
      }
      
      sections += generatePatternSection(sectionName + '_pattern', pattern, propSchema, prefix);
    }
  }
  
  return sections;
}

function generateObjectSection(name, schema, prefix = '') {
  const fullName = prefix ? `${prefix}.${name}` : name;
  let section = `\n### \`${fullName}\`\n\n`;
  section += `**Type:** object\n\n`;
  
  if (schema.description) {
    section += `${schema.description}\n\n`;
  }
  
  if (schema.properties) {
    section += generatePropertiesTable(schema.properties, schema.required || [], '####');
  }
  
  // Recursively handle nested structures
  section += generateNestedStructures(schema, fullName);
  
  return section;
}

function generateArraySection(name, schema, prefix = '') {
  const fullName = prefix ? `${prefix}.${name}` : name;
  let section = `\n### \`${fullName}\`\n\n`;
  section += `**Type:** array\n\n`;
  
  if (schema.description) {
    section += `${schema.description}\n\n`;
  }
  
  if (schema.items) {
    section += `**Array items:** ${schema.items.type || 'object'}\n\n`;
    
    if (schema.items.properties) {
      section += '**Item Properties:**\n\n';
      section += generatePropertiesTable(schema.items.properties, schema.items.required || [], '####');
    }
    
    // Recursively handle nested structures in array items
    if (schema.items.properties || schema.items.patternProperties) {
      section += generateNestedStructures(schema.items, fullName);
    }
  }
  
  return section;
}

function generatePatternSection(name, pattern, schema, prefix = '') {
  const fullName = prefix ? `${prefix}.${name}` : name;
  let section = `\n### \`${fullName}\`\n\n`;
  section += `**Type:** object (dynamic properties)\n\n`;
  section += `**Pattern:** Properties matching \`${pattern}\`\n\n`;
  
  if (schema.description) {
    section += `${schema.description}\n\n`;
  }
  
  if (schema.type === 'object' && schema.properties) {
    section += 'Each property matching this pattern must be an object with:\n\n';
    section += generatePropertiesTable(schema.properties, schema.required || [], '####');
    section += generateNestedStructures(schema, fullName);
  } else {
    // For non-object patterns, describe the expected value
    section += `Each property matching this pattern must be:\n\n`;
    section += `- **Type:** ${schema.type || 'any'}\n`;
    if (schema.description) {
      section += `- **Description:** ${schema.description}\n`;
    }
    if (schema.enum) {
      section += `- **Allowed values:** ${schema.enum.map(v => `\`${v}\``).join(', ')}\n`;
    }
  }
  
  return section;
}

function hasPropertyConstraints(prop) {
  return prop.enum || prop.pattern || prop.format || 
         prop.minLength || prop.maxLength || 
         prop.minimum !== undefined || prop.maximum !== undefined ||
         prop.default !== undefined;
}

function generateConstrainedPropertySection(name, schema, prefix = '') {
  const fullName = prefix ? `${prefix}.${name}` : name;
  let section = `\n### \`${fullName}\`\n\n`;
  section += `**Type:** ${schema.type || 'any'}\n\n`;
  
  if (schema.description) {
    section += `${schema.description}\n\n`;
  }
  
  // Add constraint details
  if (schema.enum) {
    section += `**Allowed values:**\n\n`;
    for (const value of schema.enum) {
      section += `- \`${value}\`\n`;
    }
    section += '\n';
  }
  
  if (schema.pattern) {
    section += `**Pattern:** \`${schema.pattern}\`\n\n`;
  }
  
  if (schema.format) {
    section += `**Format:** ${schema.format}\n\n`;
  }
  
  if (schema.minLength || schema.maxLength) {
    section += `**Length:** ${schema.minLength || 0} to ${schema.maxLength || '∞'} characters\n\n`;
  }
  
  // Handle minimum and maximum constraints more precisely
  if (schema.minimum !== undefined && schema.maximum !== undefined) {
    section += `**Range:** ${schema.minimum} to ${schema.maximum}\n\n`;
  } else if (schema.minimum !== undefined) {
    section += `**Minimum:** ${schema.minimum}\n\n`;
  } else if (schema.maximum !== undefined) {
    section += `**Maximum:** ${schema.maximum}\n\n`;
  }
  
  // Handle default values
  if (schema.default !== undefined) {
    section += `**Default:** \`${JSON.stringify(schema.default)}\`\n\n`;
  }
  
  return section;
}

// Generate documentation for each schema
console.log('Generating schema documentation...');

// Sort configs to find the first one (lowest weight)
const sortedConfigs = SCHEMA_CONFIGS.sort((a, b) => a.weight - b.weight);
const firstSchemaSlug = sortedConfigs[0].outputFile.replace('.md', '/');

// Update parent spec page navigation to point to first child
const specIndexPath = path.join(OUTPUT_DIR, '_index.md');
if (fs.existsSync(specIndexPath)) {
  let specContent = fs.readFileSync(specIndexPath, 'utf8');
  
  // Update or add next navigation to point to first schema page
  if (specContent.includes('next:')) {
    specContent = specContent.replace(/next:\s*[^\n]+/, `next: /docs/specs/${firstSchemaSlug}`);
  } else {
    // Add next after weight line
    specContent = specContent.replace(/(weight:\s*\d+)/, `$1\nnext: /docs/specs/${firstSchemaSlug}`);
  }
  
  fs.writeFileSync(specIndexPath, specContent, 'utf8');
  console.log('✓ Updated parent spec navigation');
}

for (const config of SCHEMA_CONFIGS) {
  try {
    const markdown = generateSchemaMarkdown(config);
    const outputPath = path.join(OUTPUT_DIR, config.outputFile);
    
    fs.writeFileSync(outputPath, markdown, 'utf8');
    console.log(`✓ Generated ${config.outputFile}`);
  } catch (error) {
    console.error(`✗ Failed to generate ${config.outputFile}:`, error.message);
    process.exit(1);
  }
}

console.log('Schema documentation generated successfully!');