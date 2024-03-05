document.addEventListener('DOMContentLoaded', async function () {
    async function processText(selectedOption, inputText) {
        try {
            // Show loading message
            document.getElementById('output-box').innerText = 'Processing...';
    
            const formData = new FormData();
            formData.append('choice', selectedOption);
            formData.append('user_input', inputText);
    
            // If selectedOption is 4 (Translate Text), include the target language in the request body
            if (selectedOption === '4') {
                const targetLanguage = document.getElementById('target_language').value;
                formData.append('target_language', targetLanguage);
            }
    
            // If selectedOption is 6 (Summarize File Content), append file data to the request
            if (selectedOption === '6') {
                const fileInput = document.getElementById('file_input');
                const file = fileInput.files[0];
                if (!file) {
                    // No file selected, display an error message and return
                    document.getElementById('output-box').innerText = 'Error: No file selected';
                    return;
                }
                formData.append('file', file);
            }
    
            const response = await fetch('/process_text', {
                method: 'POST',
                body: formData
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

        // Display or hide file input based on selected option
        if (selectedOption === '6') {
            document.getElementById('file_input_container').style.display = 'block';
        } else {
            document.getElementById('file_input_container').style.display = 'none';
        }
    });

    document.getElementById('processBtn').addEventListener('click', async function () {
        var selectedOption = document.getElementById('operation').value;
        var inputText = document.getElementById('user_input').value;

        // Call the processText function
        await processText(selectedOption, inputText);
    });
});
