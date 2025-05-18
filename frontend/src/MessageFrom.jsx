import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import axios from 'axios'

const api = axios.create({
    baseURL: "http://localhost:5173/"
})

export function MessageWithButton() {
    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Button clicked");
        const response = await api.post("/chat", {message: question})
        setAnswer(response.data.answer)
    }

    return (
        <div className="grid items-center justify-center gap-2">
            <Textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Type your message here." />
            <Button type='submit' onClick={handleSubmit} >Kirim</Button>
        </div>
    )
}
