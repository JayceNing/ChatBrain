// HTML 元素


// OpenAI API 配置
const apiUrl = "https://api.openai.com/v1/completions";
const apiKey = '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';

// 异步函数，发送 API 请求
async function generateText(prompt) {
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + "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",
            },
            body: JSON.stringify({
                prompt: prompt,
                model: "text-davinci-003",
                max_tokens: 500,
                temperature: 0,

            })
        });

        const result = await response.json();
        console.log(result)
        return result.choices[0].text;
    } catch (error) {
        console.error('API 请求出错:', error);
        return null;
    }
}

// 处理生成结果
async function handleResponse(result) {
    console.log(result)
    // if (!result.done) {
    //     const continuation = await generateText('');
    //     handleResponse(continuation);
    // } else {
    //     //loadingElement.style.display = 'none';
    // }
}

// 触发生成文本
async function startGeneration() {
    //loadingElement.style.display = 'block';
    const initialResponse = await generateText('Once upon a time');
    handleResponse(initialResponse);
}

// // 调用生成函数
// startGeneration();

export default startGeneration;
