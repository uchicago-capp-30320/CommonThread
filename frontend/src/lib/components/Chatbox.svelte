<script>
    import { onMount } from 'svelte';
    import authRequest from '$lib/authRequest.js';
    import { accessToken, refreshToken } from '$lib/store.js'; // Assuming store.js exists and exports these

    export let projectId;

    let messages = [];
    let userInput = '';
    let isLoading = false;
    let error = null;
    let messagesContainer; // For auto-scrolling

    // Function to scroll to the bottom of the messages
    const scrollToBottom = () => {
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    };

    onMount(() => {
        // Example initial message or fetch initial project data if needed
        // messages = [...messages, { id: Date.now(), text: `Chatting about project ${projectId}`, sender: 'system' }];
        scrollToBottom();
    });

    async function sendMessage() {
        if (userInput.trim() === '' || isLoading) return;

        isLoading = true;
        error = null;
        const currentUserMessage = userInput.trim();
        messages = [...messages, { id: Date.now(), text: currentUserMessage, sender: 'user' }];
        userInput = '';
        scrollToBottom(); // Scroll after adding user message

        try {
            const postData = { user_message: currentUserMessage };
            const response = await authRequest(
                `/project/${projectId}/chat`,
                'POST',
                $accessToken,
                $refreshToken,
                postData
            );

            if (response && response.data && response.data.reply) {
                messages = [...messages, { id: Date.now(), text: response.data.reply, sender: 'ai' }];
                if (response.newAccessToken) {
                    accessToken.set(response.newAccessToken);
                }
            } else if (response && response.error) { // Handle errors returned in the response body from authRequest or the API
                console.error("Error from server:", response.error);
                error = response.error.message || response.error.details || 'Failed to get reply from server.';
                messages = [...messages, { id: Date.now(), text: `Error: ${error}`, sender: 'system' }];
            } 
            else {
                throw new Error('Invalid response structure from server');
            }
        } catch (err) {
            console.error("Error sending message:", err);
            error = err.message || 'Failed to send message.';
            messages = [...messages, { id: Date.now(), text: `Error: ${error}`, sender: 'system' }];
        } finally {
            isLoading = false;
            scrollToBottom(); // Scroll after adding AI/error message
        }
    }

    // Reactive statement to scroll to bottom when messages change
    $: if (messages && messagesContainer) scrollToBottom();

</script>

<div class="chatbox">
    <div class="messages" bind:this={messagesContainer}>
        {#each messages as message (message.id)}
            <div class="message {message.sender}-message">
                {message.text}
            </div>
        {/each}
        {#if isLoading}
            <div class="message system-message">AI is thinking...</div>
        {/if}
    </div>
    {#if error}
        <div class="error-message">
            <p>Error: {error}</p>
        </div>
    {/if}
    <div class="input-area">
        <input
            type="text"
            bind:value={userInput}
            on:keydown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your message..."
            disabled={isLoading}
        />
        <button on:click={sendMessage} disabled={isLoading}>Send</button>
    </div>
</div>

<style>
    .chatbox {
        display: flex;
        flex-direction: column;
        font-family: Arial, sans-serif;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 15px;
        max-width: 500px; /* Or your preferred max-width */
        margin: 20px auto;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }

    .messages {
        height: 300px;
        overflow-y: auto;
        border: 1px solid #eee;
        padding: 10px;
        margin-bottom: 10px;
        background-color: #f9f9f9;
        border-radius: 4px;
    }

    .message {
        margin-bottom: 8px;
        padding: 10px;
        border-radius: 8px;
        line-height: 1.4;
        word-wrap: break-word;
    }

    .user-message {
        background-color: #007bff; /* Blue for user */
        color: white;
        text-align: right;
        margin-left: auto;
        max-width: 75%;
    }

    .ai-message {
        background-color: #e9ecef; /* Light grey for AI */
        color: #333;
        text-align: left;
        margin-right: auto;
        max-width: 75%;
    }

    .system-message {
        background-color: #fff3cd; /* Yellowish for system/error */
        color: #856404;
        text-align: center;
        font-style: italic;
        font-size: 0.9em;
        max-width: 100%;
    }

    .input-area {
        display: flex;
        margin-top: 10px;
    }

    .input-area input {
        flex-grow: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px 0 0 4px;
        font-size: 1em;
    }

    .input-area input:focus {
        outline: none;
        border-color: #007bff;
        box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
    }

    .input-area button {
        padding: 10px 15px;
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 0 4px 4px 0;
        cursor: pointer;
        font-size: 1em;
    }

    .input-area button:hover {
        background-color: #0056b3;
    }

    .input-area button:disabled {
        background-color: #cccccc;
        cursor: not-allowed;
    }

    .error-message {
        color: #721c24; /* Dark red for error text */
        background-color: #f8d7da; /* Light red for error background */
        border: 1px solid #f5c6cb;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 4px;
        text-align: center;
    }
</style>
