<template>
  <div
    v-if="aiAvailable"
    class="ai-chat-wrapper"
  >
    <!-- Floating button -->
    <button
      class="ai-fab"
      :class="{ hidden: isOpen }"
      aria-label="Open AI Assistant"
      @click="isOpen = true"
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        width="22"
        height="22"
      >
        <path d="M12 2a4 4 0 0 1 4 4v1h1a3 3 0 0 1 3 3v2a3 3 0 0 1-3 3h-1v1a4 4 0 0 1-8 0v-1H7a3 3 0 0 1-3-3v-2a3 3 0 0 1 3-3h1V6a4 4 0 0 1 4-4z" />
        <circle
          cx="9.5"
          cy="10.5"
          r="1"
          fill="currentColor"
        />
        <circle
          cx="14.5"
          cy="10.5"
          r="1"
          fill="currentColor"
        />
      </svg>
    </button>

    <!-- Chat panel -->
    <Transition name="chat-slide">
      <div
        v-if="isOpen"
        class="ai-panel"
      >
        <div class="ai-header">
          <div class="ai-header-left">
            <span class="ai-dot" />
            <span class="ai-title">SpaceX AI Assistant</span>
          </div>
          <button
            class="ai-close"
            aria-label="Close"
            @click="isOpen = false"
          >
            &times;
          </button>
        </div>

        <div
          ref="messagesRef"
          class="ai-messages"
        >
          <div class="ai-msg assistant">
            <p>Hi! I'm your SpaceX data assistant. Ask me anything — missions, rockets, Starlink, costs, emissions, landing operations, history, or even the Tesla Roadster in orbit.</p>
          </div>
          <div
            v-for="(msg, i) in messages"
            :key="i"
            class="ai-msg"
            :class="msg.role"
          >
            <p v-if="msg.role === 'user'">
              {{ msg.content }}
            </p>
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div
              v-else
              class="msg-formatted"
              v-html="formatMessage(msg.content, typing && i === messages.length - 1)"
            />
          </div>
          <div
            v-if="loading && !typing"
            class="ai-msg assistant"
          >
            <span class="ai-typing">
              <span class="typing-dot" />
              <span class="typing-dot" />
              <span class="typing-dot" />
            </span>
          </div>
        </div>

        <form
          class="ai-input-row"
          @submit.prevent="send"
        >
          <input
            v-model="input"
            class="ai-input"
            placeholder="Ask anything about SpaceX..."
            :disabled="loading"
            autocomplete="off"
          >
          <button
            class="ai-send"
            type="submit"
            :disabled="!input.trim() || loading"
            aria-label="Send"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              width="18"
              height="18"
            >
              <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        </form>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { fetchAiStatus, sendChatMessage } from '@/api'
import type { ChatMessage } from '@/types'

const aiAvailable = ref(false)
const isOpen = ref(false)
const loading = ref(false)
const typing = ref(false)
const input = ref('')
const messages = ref<ChatMessage[]>([])
const messagesRef = ref<HTMLElement | null>(null)

let typewriterTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  try {
    const status = await fetchAiStatus()
    aiAvailable.value = status.available
  } catch {
    aiAvailable.value = false
  }
})

onBeforeUnmount(() => {
  if (typewriterTimer) clearTimeout(typewriterTimer)
})

async function send(): Promise<void> {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const res = await sendChatMessage(text, messages.value.slice(0, -1))
    await typewriteResponse(res.response)
  } catch {
    await typewriteResponse('Something went wrong. Please try again.')
  } finally {
    loading.value = false
  }
}

function typewriteResponse(fullText: string): Promise<void> {
  return new Promise((resolve) => {
    const msg: ChatMessage = { role: 'assistant', content: '' }
    messages.value.push(msg)
    typing.value = true

    const idx = messages.value.length - 1
    let charIdx = 0
    const speed = 12

    function tick(): void {
      if (charIdx < fullText.length) {
        const chunk = fullText.slice(charIdx, charIdx + 2)
        messages.value[idx] = {
          ...messages.value[idx],
          content: messages.value[idx].content + chunk,
        }
        charIdx += 2
        scrollToBottom()
        typewriterTimer = setTimeout(tick, speed)
      } else {
        typing.value = false
        typewriterTimer = null
        scrollToBottom()
        resolve()
      }
    }

    nextTick(tick)
  })
}

function formatMessage(text: string, showCursor: boolean = false): string {
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Bold: **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Inline code: `text`
  html = html.replace(/`(.+?)`/g, '<code>$1</code>')

  // Split into lines for list processing
  const lines = html.split('\n')
  const result: string[] = []
  let inUl = false
  let inOl = false

  for (const line of lines) {
    const trimmed = line.trim()
    const ulMatch = trimmed.match(/^[-*]\s+(.+)/)
    const olMatch = trimmed.match(/^\d+\.\s+(.+)/)

    if (ulMatch) {
      if (inOl) { result.push('</ol>'); inOl = false }
      if (!inUl) { result.push('<ul>'); inUl = true }
      result.push(`<li>${ulMatch[1]}</li>`)
    } else if (olMatch) {
      if (inUl) { result.push('</ul>'); inUl = false }
      if (!inOl) { result.push('<ol>'); inOl = true }
      result.push(`<li>${olMatch[1]}</li>`)
    } else {
      if (inUl) { result.push('</ul>'); inUl = false }
      if (inOl) { result.push('</ol>'); inOl = false }
      if (trimmed === '') {
        result.push('<br>')
      } else {
        result.push(`<p>${trimmed}</p>`)
      }
    }
  }

  if (inUl) result.push('</ul>')
  if (inOl) result.push('</ol>')

  let output = result.join('')
  if (showCursor) {
    output += '<span class="typing-cursor"></span>'
  }
  return output
}

function scrollToBottom(): void {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.ai-chat-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 90;
}

/* Floating action button */
.ai-fab {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 1px solid var(--border-strong);
  background: var(--bg-surface);
  color: var(--accent);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s;
}

.ai-fab:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.35);
}

.ai-fab.hidden {
  opacity: 0;
  pointer-events: none;
  transform: scale(0.8);
}

/* Chat panel */
.ai-panel {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 360px;
  max-height: 520px;
  background: var(--bg-base);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.ai-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.ai-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--success);
  animation: pulse-ai 2s ease-in-out infinite;
}

@keyframes pulse-ai {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.ai-title {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text);
}

.ai-close {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.4rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  line-height: 1;
  transition: color 0.12s, background 0.12s;
}

.ai-close:hover {
  color: var(--text);
  background: var(--bg-hover);
}

/* Messages area */
.ai-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 300px;
  max-height: 380px;
}

.ai-msg {
  max-width: 88%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 0.88rem;
  line-height: 1.5;
}

.ai-msg p {
  margin: 0;
}

/* Formatted assistant messages */
.msg-formatted p {
  margin: 0 0 6px 0;
}

.msg-formatted p:last-child {
  margin-bottom: 0;
}

.msg-formatted br {
  display: block;
  content: '';
  margin: 4px 0;
}

.msg-formatted strong {
  color: var(--text);
  font-weight: 600;
}

.msg-formatted code {
  font-family: var(--font-mono);
  font-size: 0.82em;
  background: var(--bg-hover);
  padding: 1px 5px;
  border-radius: 3px;
}

.msg-formatted ul,
.msg-formatted ol {
  margin: 6px 0;
  padding-left: 18px;
}

.msg-formatted li {
  margin-bottom: 3px;
  line-height: 1.45;
}

.msg-formatted li:last-child {
  margin-bottom: 0;
}

.ai-msg.user {
  align-self: flex-end;
  background: var(--accent);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.ai-msg.assistant {
  align-self: flex-start;
  background: var(--bg-surface);
  color: var(--text-secondary);
  border-bottom-left-radius: 4px;
  border: 1px solid var(--border);
}

/* Typewriter cursor — uses :deep so it works inside v-html */
.ai-msg :deep(.typing-cursor) {
  display: inline-block;
  width: 2px;
  height: 1em;
  background: var(--accent);
  margin-left: 1px;
  vertical-align: text-bottom;
  animation: blink-cursor 0.7s steps(1) infinite;
}

@keyframes blink-cursor {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* Typing indicator */
.ai-typing {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing-bounce 1.2s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.15s; }
.typing-dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes typing-bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-4px); opacity: 1; }
}

/* Input row */
.ai-input-row {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}

.ai-input {
  flex: 1;
  min-width: 0;
  padding: 10px 14px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  background: var(--bg-input);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 0.88rem;
  outline: none;
  transition: border-color 0.15s;
}

.ai-input::placeholder {
  color: var(--text-muted);
}

.ai-input:focus {
  border-color: var(--accent);
}

.ai-send {
  width: 40px;
  height: 40px;
  border-radius: var(--radius);
  border: 1px solid var(--border-strong);
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.15s, transform 0.15s;
  flex-shrink: 0;
}

.ai-send:hover:not(:disabled) {
  transform: scale(1.05);
}

.ai-send:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* Slide transition */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
}

/* Responsive */
@media (max-width: 640px) {
  .ai-panel {
    bottom: 0;
    right: 0;
    left: 0;
    width: 100%;
    max-height: 85vh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    box-sizing: border-box;
  }

  .ai-input-row {
    padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  }

  .ai-chat-wrapper {
    bottom: 16px;
    right: 16px;
  }

  .ai-fab {
    width: 48px;
    height: 48px;
  }
}
</style>
