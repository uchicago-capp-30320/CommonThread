// Chatbox.test.js
import { writable } from 'svelte/store';
import { vi } from 'vitest';

// Mock Svelte stores from $lib/store.js
const mockAccessToken = writable('fake-access-token');
const mockRefreshToken = writable('fake-refresh-token');
vi.mock('$lib/store.js', () => ({
    __esModule: true, // This is important for ES Modules
    accessToken: mockAccessToken,
    refreshToken: mockRefreshToken,
    // Mock other exports from store.js if Chatbox uses them, else they can be undefined or vi.fn()
    // For example, if store.js also exports an 'ipAddress' store:
    ipAddress: writable('http://localhost:8000') 
}));

// Mock authRequest
vi.mock('$lib/authRequest.js', () => ({
    __esModule: true,
    authRequest: vi.fn()
}));

// Now the tests...
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import Chatbox from './Chatbox.svelte'; // Path to component

describe('Chatbox.svelte', () => {
    const projectId = 'test-project-123';
    let authRequestMock;

    beforeEach(async () => {
        vi.clearAllMocks(); // Clear all mocks

        // Re-import the mocked authRequest to get the vi.fn() instance for this test scope
        const authRequestModule = await import('$lib/authRequest.js');
        authRequestMock = authRequestModule.authRequest;

        authRequestMock.mockResolvedValue({ // Default mock for successful calls
            data: { reply: "Mocked AI response" },
            newAccessToken: null
        });

        // Reset store values
        mockAccessToken.set('fake-access-token');
        mockRefreshToken.set('fake-refresh-token');
    });

    test('renders initial state correctly', () => {
        render(Chatbox, { props: { projectId } });
        expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument();
    });

    test('sends a message and displays user and AI responses', async () => {
        render(Chatbox, { props: { projectId } });

        const input = screen.getByPlaceholderText('Type your message...');
        const sendButton = screen.getByRole('button', { name: 'Send' });

        await fireEvent.input(input, { target: { value: 'Hello AI' } });
        await fireEvent.click(sendButton);

        // Check if user message appears
        // Note: The component wraps messages in divs with class based on sender.
        // We can check for the text content within elements having the 'user-message' class.
        const userMessages = screen.getAllByText('Hello AI');
        expect(userMessages.some(el => el.closest('.user-message'))).toBe(true);


        // Check if authRequest was called
        expect(authRequestMock).toHaveBeenCalledWith(
            `/project/${projectId}/chat`,
            'POST',
            'fake-access-token', // This comes from the mockAccessToken
            'fake-refresh-token', // This comes from the mockRefreshToken
            { user_message: 'Hello AI' }
        );

        // Wait for AI response to appear
        await waitFor(() => {
             const aiMessages = screen.getAllByText('Mocked AI response');
             expect(aiMessages.some(el => el.closest('.ai-message'))).toBe(true);
        });

        // Check if input is cleared
        expect(input.value).toBe('');
    });

    test('shows loading indicator while sending message', async () => {
        authRequestMock.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({ data: { reply: "Done" } }), 100))); // Delayed response

        render(Chatbox, { props: { projectId } });
        const input = screen.getByPlaceholderText('Type your message...');
        await fireEvent.input(input, { target: { value: 'Test loading' } });
        await fireEvent.click(screen.getByRole('button', { name: 'Send' }));
        
        // User message should be visible
        const userMessages = screen.getAllByText('Test loading');
        expect(userMessages.some(el => el.closest('.user-message'))).toBe(true);

        // Check for loading message (AI is thinking...)
        expect(screen.getByText('AI is thinking...')).toBeInTheDocument();
        // Check if send button is disabled
        expect(screen.getByRole('button', { name: 'Send' })).toBeDisabled();


        await waitFor(() => {
            const aiMessages = screen.getAllByText('Done');
            expect(aiMessages.some(el => el.closest('.ai-message'))).toBe(true);
        });
        expect(screen.getByRole('button', { name: 'Send' })).not.toBeDisabled();
        // Ensure "AI is thinking..." message is gone
        expect(screen.queryByText('AI is thinking...')).not.toBeInTheDocument();
    });

    test('displays error message if sending fails due to network/server error', async () => {
        authRequestMock.mockRejectedValue(new Error('Network Error'));

        render(Chatbox, { props: { projectId } });
        const input = screen.getByPlaceholderText('Type your message...');
        await fireEvent.input(input, { target: { value: 'Error test' } });
        await fireEvent.click(screen.getByRole('button', { name: 'Send' }));

        await waitFor(() => {
            // The component adds "Error: " + error message to messages array with sender 'system'
            const errorMessages = screen.getAllByText('Error: Network Error');
            expect(errorMessages.some(el => el.closest('.system-message'))).toBe(true);
        });
         // Also check the dedicated error display area
        expect(screen.getByText('Error: Network Error', { selector: '.error-message p' })).toBeInTheDocument();
    });
    
    test('displays error message if API returns an error structure', async () => {
        authRequestMock.mockResolvedValue({ 
            error: { message: "API Error Detail" } 
        });

        render(Chatbox, { props: { projectId } });
        const input = screen.getByPlaceholderText('Type your message...');
        await fireEvent.input(input, { target: { value: 'API error test' } });
        await fireEvent.click(screen.getByRole('button', { name: 'Send' }));

        await waitFor(() => {
            const errorMessages = screen.getAllByText('Error: API Error Detail');
            expect(errorMessages.some(el => el.closest('.system-message'))).toBe(true);
        });
        // Also check the dedicated error display area
        expect(screen.getByText('Error: API Error Detail', { selector: '.error-message p' })).toBeInTheDocument();
    });


    test('does not send message if input is empty', async () => {
        render(Chatbox, { props: { projectId } });
        
        const sendButton = screen.getByRole('button', { name: 'Send' });
        await fireEvent.click(sendButton);

        expect(authRequestMock).not.toHaveBeenCalled();
    });

    test('updates access token if new one is received', async () => {
        authRequestMock.mockResolvedValue({
            data: { reply: "Response with new token" },
            newAccessToken: 'new-fake-access-token'
        });

        render(Chatbox, { props: { projectId } });
        const input = screen.getByPlaceholderText('Type your message...');
        await fireEvent.input(input, { target: { value: 'Token refresh test' } });
        await fireEvent.click(screen.getByRole('button', { name: 'Send' }));

        await waitFor(() => {
            expect(screen.getByText('Response with new token')).toBeInTheDocument();
        });
        
        let currentTokenValue;
        const unsubscribe = mockAccessToken.subscribe(value => { // Subscribe to the Svelte store
            currentTokenValue = value;
        });
        unsubscribe(); // Immediately unsubscribe after getting the value
        
        expect(currentTokenValue).toBe('new-fake-access-token');
    });
});
