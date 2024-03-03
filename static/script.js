document.addEventListener('DOMContentLoaded', async function () {
    async function processText(selectedOption, inputText) {
        try {
            // Show loading message
            document.getElementById('output-box').innerText = 'Processing...';

            let body = `user_input=${encodeURIComponent(inputText)}&choice=${selectedOption}`;

            // If selectedOption is 4 (Translate Text), include the target language in the request body
            if (selectedOption === '4') {
                const targetLanguage = document.getElementById('target_language').value;
                body += `&target_language=${targetLanguage}`;
            }

            const response = await fetch('/process_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: body
            });

            const data = await response.json();

            // Hide loading message and display the result
            document.getElementById('output-box').innerText = JSON.stringify(data, null, 2);
        } catch (error) {
            console.error('Error:', error);
        }
    }

    document.getElementById('operation').addEventListener('change', function () {
        var selectedOption = this.value;

        // Display or hide target language dropdown based on selected option
        if (selectedOption === '4') {
            document.getElementById('target_language_container').style.display = 'block';
        } else {
            document.getElementById('target_language_container').style.display = 'none';
        }
    });

    document.getElementById('processBtn').addEventListener('click', async function () {
        var selectedOption = document.getElementById('operation').value;
        var inputText = document.getElementById('user_input').value;

        // Call the processText function
        await processText(selectedOption, inputText);
    });
});
