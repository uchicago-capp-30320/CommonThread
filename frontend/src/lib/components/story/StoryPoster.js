// Create a services directory if it doesn't exist
export async function submitStory(storyData) {
	try {
		console.log('Sending data:', storyData);

		const response = await fetch('http://127.0.0.1:8000/stories/create/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(storyData)
		});

		if (!response.ok) {
			const errorData = await response.json();
			throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
		}

		const cleared_response = await response.json();
		console.log(cleared_response);
		return cleared_response;
	} catch (error) {
		console.error('Error submitting story:', error);
		throw error;
	}
}
