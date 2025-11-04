import * as vscode from 'vscode';
import { OCPAgent, OCPContextDict } from '@opencontext/agent';

// Singleton OCPAgent instance for the workspace
let ocpAgent: OCPAgent | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('OCP extension is now active');

    // Initialize OCPAgent with VS Code settings
    const config = vscode.workspace.getConfiguration('ocp');
    const user = config.get<string>('user') || process.env.USER || 'unknown';
    const registryUrl = config.get<string>('registryUrl') || 'https://registry.opencontextprotocol.org';
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    const workspace = workspaceFolder?.name || 'unknown';

    // Create the singleton OCPAgent instance
    ocpAgent = new OCPAgent(
        'vscode-extension',
        user,
        workspace,
        'Assist with development tasks',
        registryUrl
    );

    console.log(`OCP Agent initialized for user "${user}" in workspace "${workspace}"`);

    // Register Language Model Tool: getContext
    const getContextTool = vscode.lm.registerTool('ocp_getContext', {
        invoke: async (options: vscode.LanguageModelToolInvocationOptions<{}>, token: vscode.CancellationToken) => {
            try {
                if (!ocpAgent) {
                    return new vscode.LanguageModelToolResult([
                        new vscode.LanguageModelTextPart(JSON.stringify({
                            error: "OCP Agent not initialized"
                        }))
                    ]);
                }

                const contextDict: OCPContextDict = ocpAgent.context.toDict();
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify(contextDict, null, 2))
                ]);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({ error: errorMessage }))
                ]);
            }
        }
    });

    context.subscriptions.push(getContextTool);

    // Register Language Model Tool: registerApi
    const registerApiTool = vscode.lm.registerTool('ocp_registerApi', {
        invoke: async (options: vscode.LanguageModelToolInvocationOptions<{
            name: string;
            specUrl?: string;
            baseUrl?: string;
        }>, token: vscode.CancellationToken) => {
            try {
                if (!ocpAgent) {
                    return new vscode.LanguageModelToolResult([
                        new vscode.LanguageModelTextPart(JSON.stringify({
                            error: "OCP Agent not initialized"
                        }))
                    ]);
                }

                const params = options.input;

                // Get auth headers for this API if configured
                const config = vscode.workspace.getConfiguration('ocp');
                const apiAuth = config.get<Record<string, Record<string, string>>>('apiAuth') || {};
                const authHeaders = apiAuth[params.name];

                await ocpAgent.registerApi(params.name, params.specUrl, params.baseUrl);
                
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({
                        success: true,
                        message: `Registered API: ${params.name}`,
                        hasAuth: !!authHeaders
                    }, null, 2))
                ]);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({ error: errorMessage }))
                ]);
            }
        }
    });

    context.subscriptions.push(registerApiTool);

    // Register Language Model Tool: listTools
    const listToolsTool = vscode.lm.registerTool('ocp_listTools', {
        invoke: async (options: vscode.LanguageModelToolInvocationOptions<{
            apiName?: string;
        }>, token: vscode.CancellationToken) => {
            try {
                if (!ocpAgent) {
                    return new vscode.LanguageModelToolResult([
                        new vscode.LanguageModelTextPart(JSON.stringify({
                            error: "OCP Agent not initialized"
                        }))
                    ]);
                }

                const params = options.input;
                const tools = ocpAgent.listTools(params.apiName);
                
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({
                        tools,
                        count: tools.length,
                        apiName: params.apiName || "all"
                    }, null, 2))
                ]);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({ error: errorMessage }))
                ]);
            }
        }
    });

    context.subscriptions.push(listToolsTool);

    // Register Language Model Tool: callTool
    const callToolTool = vscode.lm.registerTool('ocp_callTool', {
        invoke: async (options: vscode.LanguageModelToolInvocationOptions<{
            toolName: string;
            parameters: Record<string, any>;
            apiName?: string;
        }>, token: vscode.CancellationToken) => {
            try {
                if (!ocpAgent) {
                    return new vscode.LanguageModelToolResult([
                        new vscode.LanguageModelTextPart(JSON.stringify({
                            error: "OCP Agent not initialized"
                        }))
                    ]);
                }

                const params = options.input;
                const result = await ocpAgent.callTool(
                    params.toolName,
                    params.parameters,
                    params.apiName
                );
                
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify(result, null, 2))
                ]);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({ error: errorMessage }))
                ]);
            }
        }
    });

    context.subscriptions.push(callToolTool);

    // Register Language Model Tool: searchTools
    const searchToolsTool = vscode.lm.registerTool('ocp_searchTools', {
        invoke: async (options: vscode.LanguageModelToolInvocationOptions<{
            query: string;
            apiName?: string;
        }>, token: vscode.CancellationToken) => {
            try {
                if (!ocpAgent) {
                    return new vscode.LanguageModelToolResult([
                        new vscode.LanguageModelTextPart(JSON.stringify({
                            error: "OCP Agent not initialized"
                        }))
                    ]);
                }

                const params = options.input;
                const tools = ocpAgent.searchTools(params.query, params.apiName);
                
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({
                        tools,
                        count: tools.length,
                        query: params.query,
                        apiName: params.apiName || "all"
                    }, null, 2))
                ]);
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : String(error);
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(JSON.stringify({ error: errorMessage }))
                ]);
            }
        }
    });

    context.subscriptions.push(searchToolsTool);

    // Register Chat Participant that automatically provides OCP tools to language models
    const participant = vscode.chat.createChatParticipant('chat.ocp', async (
        request: vscode.ChatRequest,
        chatContext: vscode.ChatContext,
        stream: vscode.ChatResponseStream,
        token: vscode.CancellationToken
    ) => {
        try {
            // Get all OCP tools
            const ocpTools = vscode.lm.tools.filter(tool => tool.name.startsWith('ocp_'));
            
            // Use the model selected by the user in the chat interface
            const model = request.model;
            
            // Build messages for the chat request
            const messages = [
                vscode.LanguageModelChatMessage.User(request.prompt)
            ];
            
            // Make chat request with OCP tools automatically available
            const chatResponse = await model.sendRequest(messages, { tools: ocpTools }, token);
            
            // Process the response stream
            for await (const fragment of chatResponse.stream) {
                if (fragment instanceof vscode.LanguageModelTextPart) {
                    stream.markdown(fragment.value);
                } else if (fragment instanceof vscode.LanguageModelToolCallPart) {
                    // The LLM wants to call a tool - invoke it
                    stream.markdown(`\n\n🔧 **Calling tool:** \`${fragment.name}\`\n\n`);
                    
                    const toolResult = await vscode.lm.invokeTool(
                        fragment.name,
                        {
                            input: fragment.input,
                            toolInvocationToken: undefined
                        },
                        token
                    );
                    
                    // Add tool call and result to message history and continue the conversation
                    messages.push(vscode.LanguageModelChatMessage.Assistant([fragment]));
                    messages.push(vscode.LanguageModelChatMessage.User([
                        new vscode.LanguageModelToolResultPart(fragment.callId, toolResult.content)
                    ]));
                    
                    // Continue the chat with tool result
                    const followupResponse = await model.sendRequest(messages, { tools: ocpTools }, token);
                    for await (const followupFragment of followupResponse.stream) {
                        if (followupFragment instanceof vscode.LanguageModelTextPart) {
                            stream.markdown(followupFragment.value);
                        }
                    }
                }
            }
            
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            stream.markdown(`❌ **Error:** ${errorMessage}`);
        }
    });

    participant.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');

    context.subscriptions.push(participant);
}

export function deactivate() {}
