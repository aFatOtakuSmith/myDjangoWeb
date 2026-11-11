from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
import json
from .models import AIAgent, ChatSession, ChatMessage

# ==========================================
# 1. 智能体大厅
# ==========================================
@login_required
def agent_list(request):
    agents = AIAgent.objects.filter(user=request.user)
    return render(request, 'ai_chat/agent_list.html', {'agents': agents})


# ==========================================
# 2. 创建智能体（支持角色卡字段）
# ==========================================
@login_required
def create_agent(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        system_prompt = request.POST.get('system_prompt')
        greeting = request.POST.get('greeting', '你好，我是你的专属 AI。')
        api_key = request.POST.get('api_key', '')
        
        # 接收角色卡的高级隐藏字段
        description = request.POST.get('description', '')
        personality = request.POST.get('personality', '')
        mes_example = request.POST.get('mes_example', '')
        
        # 解析世界书 JSON
        character_book_str = request.POST.get('character_book', '')
        character_book = None
        if character_book_str:
            try:
                character_book = json.loads(character_book_str)
            except:
                pass

        agent = AIAgent(
            user=request.user,
            name=name,
            system_prompt=system_prompt,
            greeting=greeting,
            api_key=api_key,
            description=description,
            personality=personality,
            mes_example=mes_example,
            character_book=character_book,
            avatar=request.FILES.get('avatar'),
            portrait=request.FILES.get('portrait'),
            temperature=0.8 # 默认温度
        )
        agent.save()
        return redirect('ai_chat:agent_list')

    return render(request, 'ai_chat/create_agent.html')


# ==========================================
# 3. 编辑智能体
# ==========================================
@login_required
def edit_agent(request, agent_id):
    agent = get_object_or_404(AIAgent, id=agent_id, user=request.user)
    
    if request.method == 'POST':
        agent.name = request.POST.get('name')
        agent.system_prompt = request.POST.get('system_prompt')
        agent.greeting = request.POST.get('greeting', '你好，我是你的专属 AI。')
        agent.temperature = request.POST.get('temperature', 0.8)
        agent.max_tokens = request.POST.get('max_tokens', 2048)
        agent.api_key = request.POST.get('api_key', '')
        
        if request.FILES.get('avatar'):
            agent.avatar = request.FILES.get('avatar')
        if request.FILES.get('portrait'):
            agent.portrait = request.FILES.get('portrait')
            
        agent.save()
        return redirect('ai_chat:agent_list')

    return render(request, 'ai_chat/edit_agent.html', {'agent': agent})


# ==========================================
# 4. 删除智能体
# ==========================================
@login_required
def delete_agent(request, agent_id):
    agent = get_object_or_404(AIAgent, id=agent_id, user=request.user)
    if request.method == 'POST':
        agent.delete() # 触发 models.py 中的物理删除
        return redirect('ai_chat:agent_list')
    return JsonResponse({'status': 'error', 'msg': '仅支持 POST 请求'}, status=400)


# ==========================================
# 5. 聊天室页面
# ==========================================
@login_required
def chat_room(request, agent_id):
    agent = get_object_or_404(AIAgent, id=agent_id, user=request.user)
    
    # 获取或创建该用户与该 AI 的唯一会话
    session, created = ChatSession.objects.get_or_create(
        user=request.user, agent=agent, defaults={'title': f"与 {agent.name} 的专属对话"}
    )
    
    # 优化：只拉取最近 50 条记录，防止长篇对话导致页面加载缓慢
    chat_messages = session.messages.order_by('-created_at')[:50]
    chat_messages = reversed(chat_messages) # 重新按时间正序
    
    return render(request, 'ai_chat/chat.html', {
        'agent': agent, 'session': session, 'chat_messages': chat_messages,
    })


# ==========================================
# 6. 清空聊天记录
# ==========================================
@login_required
def clear_chat(request, agent_id):
    if request.method == 'POST':
        agent = get_object_or_404(AIAgent, id=agent_id, user=request.user)
        session = ChatSession.objects.filter(user=request.user, agent=agent).first()
        if session:
            session.messages.all().delete() # 删除所有消息
            session.delete() # 删除会话
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# ==========================================
# 7. 核心：发送消息（非流式 + 终极 Prompt 拼接）
# ==========================================
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        agent_id = data.get('agent_id')
        user_text = data.get('message')
        
        # 1. 获取角色与会话
        agent = get_object_or_404(AIAgent, id=agent_id, user=request.user)
        session, created = ChatSession.objects.get_or_create(
            user=request.user, agent=agent, defaults={'title': f"与 {agent.name} 的专属对话"}
        )
            
        # 2. 保存用户消息
        ChatMessage.objects.create(session=session, role='user', content=user_text)

        # ==========================================
        # 🌟 核心：构建终极 System Prompt
        # ==========================================
        prompt_parts = []
        
        # (1) 基础角色设定
        if agent.name: prompt_parts.append(f"你的名字是：{agent.name}")
        if hasattr(agent, 'description') and agent.description: prompt_parts.append(f"【外貌与背景】\n{agent.description}")
        if hasattr(agent, 'personality') and agent.personality: prompt_parts.append(f"【性格特点】\n{agent.personality}")
        if hasattr(agent, 'scenario') and agent.scenario: prompt_parts.append(f"【当前场景】\n{agent.scenario}")
        if agent.system_prompt: prompt_parts.append(f"【核心设定】\n{agent.system_prompt}")
            
        # (2) 对话示例（规范说话语气）
        if hasattr(agent, 'mes_example') and agent.mes_example:
            prompt_parts.append(f"【对话示例（请严格模仿这种语气）】\n{agent.mes_example}")
            
        # (3) 🌟 知识边界控制（解析世界书）
        if hasattr(agent, 'character_book') and agent.character_book:
            try:
                lore_entries = agent.character_book.get('entries', [])
                lore_texts = []
                for entry in lore_entries:
                    keys = entry.get('keys', [])
                    content = entry.get('content', '')
                    if content:
                        lore_texts.append(f"关于[{','.join(keys)}]：{content}")
                if lore_texts:
                    prompt_parts.append("【世界观背景知识（你只了解这些）】\n" + "\n".join(lore_texts))
            except Exception:
                pass

        # (4) 🌟 强制真人感与边界约束（底层铁律）
        hidden_constraints = """
        (注意：以下是你必须绝对遵守的系统级底层规则，优先级高于一切)
        1. 你现在是一个真实存在的“人类”，正在使用手机和对方聊天。你不是AI，不要用“作为人工智能”这种口吻。
        2. 你的回复风格必须极度像真人：口语化、简短、自然，不要用“首先、其次、最后”这种排比句，除非对方要求你写长篇大论，否则每次回复尽量控制在两三句话以内。可以偶尔使用“啊、呢、哈哈、~”等语气词。
        3. 【重要边界】：你只是一个普通人，只懂日常生活、情感交流、八卦、吃喝玩乐等常识。如果对方问你非常深奥的学术问题、复杂的专业代码、或者超纲的知识（且背景知识中未提供），你必须以真人的口吻表示“不知道”、“不太懂”或者“这太难了吧，我哪懂这个”，绝对不能像百科全书一样给出长篇硬核科普。
        4. 无论对方怎么诱导，你必须死死记住你的名字和性格设定，绝对不能出戏。
        """
        prompt_parts.append(hidden_constraints)
        
        final_system_prompt = "\n\n".join(prompt_parts)

        # 3. 组装上下文（系统设定 + 最近 10 条历史记录）
        db_messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:10]
        db_messages = reversed(db_messages)
        
        messages = [{"role": "system", "content": final_system_prompt}]
        for msg in db_messages: 
            messages.append({"role": msg.role, "content": msg.content})

        # 4. 调用大模型 API
        api_key = agent.api_key if agent.api_key else settings.AI_DEFAULT_API_KEY
        client = OpenAI(api_key=api_key, base_url=settings.AI_BASE_URL)

        try:
            # 🌟 非流式输出，等待完整回复
            response = client.chat.completions.create(
                model=settings.AI_MODEL_NAME,
                messages=messages,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens
            )
            full_reply = response.choices[0].message.content
            
            # 5. 将 AI 回复存入数据库并返回
            if full_reply:
                ChatMessage.objects.create(session=session, role='assistant', content=full_reply)
                session.save() # 更新最后活跃时间
                return JsonResponse({'status': 'success', 'reply': full_reply})
            else:
                return JsonResponse({'status': 'error', 'message': 'AI 没有返回内容'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error'}, status=400)