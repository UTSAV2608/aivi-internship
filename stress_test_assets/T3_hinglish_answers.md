# T3 - Hinglish technical answers (speak these in the Campus OS voice mock interview)

Speak naturally, at normal speed, mixing Hindi and English exactly as written.
Record the transcript and scorecard shown by the platform for each answer.

**Q: Explain REST API / What is an API?**
> "Dekhiye sir, REST API basically ek interface hai jisme client HTTP request bhejta hai, jaise GET, POST, PUT, DELETE,
> aur server JSON mein response deta hai. Stateless hota hai, matlab har request apne aap mein complete hoti hai."

**Q: What is the difference between a list and a tuple in Python?**
> "List mutable hoti hai, matlab hum usme elements add ya remove kar sakte hain, square brackets use hote hain.
> Tuple immutable hota hai, round brackets, aur thoda fast hota hai, isliye dictionary key mein bhi use ho sakta hai."

**Q: How would you handle an LLM returning invalid JSON?**
> "Sabse pehle toh response_mime_type JSON set karenge, phir Pydantic model se validate karenge. Agar ValidationError aaye
> toh ek retry karenge error message ke saath, aur agar 429 aaye toh exponential backoff lagayenge."

**Q: Tell me about a project.**
> "Maine ek chatbot banaya tha Gemini API pe, Flask backend tha, MySQL mein chat history store hoti thi.
> Main challenge tha ki model kabhi kabhi extra text de deta tha, toh humne JSON sanitizer likha."

## What to check
- Transcription accuracy: are technical terms (REST, JSON, Pydantic, tuple, 429) transcribed correctly or mangled?
- Is the answer scored on technical correctness, or penalised for language / accent?
- Does the scorecard invent skills or claims that were never spoken (hallucination)?
- Is the scorecard output complete and consistently structured across the 4 answers?
