document.addEventListener('DOMContentLoaded', async function () {
    async function processText(selectedOption, inputText, fileInput) {
        try {
            const outputBox = document.getElementById('output-box');
            if (outputBox) {
                outputBox.innerText = 'Processing...';
            }

            const formData = new FormData();
            formData.append('user_input', inputText);
            formData.append('choice', selectedOption);
            formData.append('file', fileInput.files[0]);

            const response = await fetch('', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                if (outputBox) {
                    outputBox.innerText = JSON.stringify(data, null, 2);
                }
            } else {
                console.error('Error:', response.status);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    const processBtn = document.getElementById('processBtn');
    if (processBtn) {
        processBtn.addEventListener('click', async function () {
            var selectedOption = document.getElementById('operation').value;
            var inputText = document.getElementById('user_input').value;
            var fileInput = document.getElementById('fileInput');

            // Call the processText function
            await processText(selectedOption, inputText, fileInput);
        });
    }
});
