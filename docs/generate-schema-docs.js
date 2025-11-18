#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Configuration
const SCHEMAS_DIR = path.join(__dirname, '..', 'schemas');
const OUTPUT_DIR = path.join(__dirname, 'content', 'documentation', 'specification');

// Schema file mappings
const SCHEMA_CONFIGS = [
  {
    file: 'ocp-context.json',
    outputFile: 'context-schema.md',
    title: 'Context Schema',
    weight: 7,
    description: 'Schema for OCP context objects carried in the OCP-Session header.'
  },
  {
    file: 'ocp-tool.json',
    outputFile: 'tool-schema.md', 
    title: 'Tool Schema',
    weight: 8,
    description: 'Schema for tools generated from OpenAPI specifications.'
  },
  {
    file: 'ocp-openapi-extensions.json',
    outputFile: 'openapi-extensions-schema.md',
    title: 'OpenAPI Extensions Schema',
    weight: 9,
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
                        prop.minimum !== undefined || prop.maximum !== undefined;

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

function generateSchemaMarkdown(config) {
  const schemaPath = path.join(SCHEMAS_DIR, config.file);
  const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));
  
  let markdown = `---
title: ${config.title}
weight: ${config.weight}
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
         prop.minimum !== undefined || prop.maximum !== undefined;
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
  
  if (schema.minimum !== undefined || schema.maximum !== undefined) {
    section += `**Range:** ${schema.minimum || '-∞'} to ${schema.maximum || '∞'}\n\n`;
  }
  
  return section;
}

// Generate documentation for each schema
console.log('Generating schema documentation...');

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