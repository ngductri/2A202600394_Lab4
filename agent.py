import os
from datetime import datetime
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CẤU HÌNH LOGGING
# ==========================================
LOG_DIR = "logs"
# Tự động tạo thư mục 'logs' nếu chưa tồn tại
os.makedirs(LOG_DIR, exist_ok=True) 

# Đặt tên file log theo thời gian thực (tránh trùng lặp giữa các lần chạy)
session_time = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"session_{session_time}.txt")

def write_log(role: str, content: str):
    """Hàm ghi thông tin vào file log"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%H:%M:%S")
        f.write(f"[{timestamp}] {role}:\n{content}\n")
        f.write("-" * 50 + "\n")
# ==========================================

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite-preview",
    temperature=0.2,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    
    # Lấy thời gian thực của máy tính
    current_now = datetime.now()
    current_date_str = current_now.strftime("%d/%m/%Y")
    current_time_str = current_now.strftime("%H:%M")
    
    # Tạo chuỗi ngữ cảnh thời gian động
    time_context = f"<context>\n- Hôm nay là ngày: {current_date_str}\n- Giờ hiện tại: {current_time_str}\n</context>\n\n"
    dynamic_prompt = time_context + SYSTEM_PROMPT

    # Cập nhật System Message để luôn có giờ mới nhất
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=dynamic_prompt)] + messages
    else:
        messages[0] = SystemMessage(content=dynamic_prompt)

    response = llm_with_tools.invoke(messages)

    # === LOGGING ===
    if response.tool_calls:
        for tc in response.tool_calls:
            msg = f"Gọi tool: {tc['name']}({tc['args']})"
            print(msg)
            write_log("SYSTEM (Tool Call)", msg) # Lưu log thao tác gọi tool
    else:
        print(f"Trả lời trực tiếp")

    return {"messages": [response]}

# 5. Xây dựng Graph
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()

# 6. Chat loop 
if __name__ == "__main__":
    greeting_msg = "Chào bạn! Mình là trợ lý du lịch TravelBuddy ✈️\nBạn đang muốn đi đâu hoặc có ngân sách bao nhiêu? 😊"
    
    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print(f"  Log session đang được lưu tại: {LOG_FILE}")
    print("  Gõ 'quit' để thoát")
    print("=" * 60)

    print(f"\nTravelBuddy:\n{greeting_msg}")
    write_log("TravelBuddy (Greeting)", greeting_msg) # Ghi log lời chào

    chat_history = []
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            write_log("SYSTEM", "Người dùng đã ngắt kết nối.")
            break
            
        write_log("User", user_input) # Ghi log câu hỏi của user
        
        print("\nTravelBuddy đang suy nghĩ...")
        
        chat_history.append(("human", user_input))
        
        # Thêm khối Try-Except để bắt lỗi rớt mạng hoặc lỗi API Timeout
        try:
            result = graph.invoke({"messages": chat_history})
            chat_history = result["messages"]
            final = chat_history[-1]
            
            # Xử lý format trả về (Đảm bảo KHÔNG BAO GIỜ in list)
            text = ""
            if isinstance(final.content, list):
                for item in final.content:
                    if isinstance(item, dict) and "text" in item:
                        text += item["text"] + " "
                    elif isinstance(item, str): # Bắt thêm trường hợp item là string thuần
                        text += item + " "
            else:
                text = str(final.content)
            
            text = text.strip()
            
            # Đảm bảo có nội dung in ra màn hình ngay cả khi Agent đang xử lý ngầm (gọi tool)
            if not text:
                text = "(Đang tra cứu dữ liệu...)"
                
            print(f"\nTravelBuddy: {text}")
            write_log("TravelBuddy", text) # Ghi log câu trả lời của Agent

        except Exception as e:
            error_msg = "Xin lỗi bạn, đường truyền mạng đến máy chủ bị gián đoạn (Network Error). Bạn vui lòng nhập lại câu hỏi nhé!"
            print(f"\nTravelBuddy: {error_msg}")
            write_log("SYSTEM ERROR", str(e))
            
            if chat_history and chat_history[-1][0] == "human":
                chat_history.pop()