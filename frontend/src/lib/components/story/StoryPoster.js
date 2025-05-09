// Create a services directory if it doesn't exist
export async function submitStory(storyData) {
    try {
        // Convert the data to the format expected by the backend with hardcoded IDs
        const requestData = {
            storyteller: storyData.storyteller,
            content: storyData.content,
            proj_id: 1,  // Hardcoded project ID
            curator: 1,   
            tags: storyData.tags?.map(tag => ({
                name: tag.category,
                value: tag.value
            })) || []
        };

        console.log('Sending data:', requestData); 

        const response = await fetch('http://127.0.0.1:8000/stories/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        const cleared_response =  await response.json();
        console.log(cleared_response);
        return cleared_response;

    } catch (error) {
        console.error('Error submitting story:', error);
        throw error;
    }
}