import gradio as gr
import logging
import AI_mentor_framework

class GrDemo():
    def __init__(self):
        self.customer = AI_mentor_framework.Chatbot("role_customer", "")
    def customerChat(self, question, history):
        answer = self.customer.chat(question)
        history.append((question, answer))
        return gr.update(value=""), history
    def clickButton(self, button):
        mentor = AI_mentor_framework.Chatbot("role_mentor", self.customer.chat_history)
        answer = mentor.chat("請評價我作為理專與顧客對話的表現")
        return answer

with gr.Blocks() as demo:
    grDemo = GrDemo()
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="您的回覆")
            judge_button = gr.Button(value="AI評論")
            
        with gr.Column():
            gr.Markdown(
                value="""
                # 客戶 Profile
                姓名: 王大明 \n
                性別: 男 \n
                年齡: 67歲 \n
                資產: 100萬美金 \n
                風屬: 風險趨避 \n
                個性: 自大 \n
                """
            )
            summary = gr.Textbox(label="對練總評")
        msg.submit(
                fn=grDemo.customerChat, 
                inputs=[msg, chatbot],
                outputs=[msg, chatbot], 
                queue=False
        )
        judge_button.click(
                fn=grDemo.clickButton,
                inputs=judge_button,
                outputs=[summary]
        )

if __name__ == "__main__":
    demo.launch(share=True)