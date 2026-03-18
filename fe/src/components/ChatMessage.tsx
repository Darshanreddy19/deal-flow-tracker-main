import { motion } from "framer-motion";
import { Bot, Mail, MessageSquare, ThumbsUp, ThumbsDown, Minus } from "lucide-react";
import { Message } from "@/data/types";

interface ChatMessageProps {
  message: Message;
  index: number;
}

const sentimentIcons = {
  positive: { icon: ThumbsUp, className: "text-accent" },
  neutral: { icon: Minus, className: "text-muted-foreground" },
  negative: { icon: ThumbsDown, className: "text-destructive" },
};

type SenderRole = "sber" | "russian" | "indian" | "system";

const RUSSIAN_ORGS = [
  "severstal", "r-pharm", "rosneft", "medcorp", "main chain",
  "unifrost", "northern steel", "stupino", "russian builder",
  "moscow e-market", "ministry of health",
];

function getSenderRole(sender: string, type: string): SenderRole {
  if (type === "system") return "system";
  const s = sender.toLowerCase();
  if (s.includes("sber") || s.includes("you (")) return "sber";
  if (RUSSIAN_ORGS.some((org) => s.includes(org))) return "russian";
  return "indian";
}

const roleConfig = {
  sber: {
    label: "SBER BD",
    avatarBg: "bg-primary/15 border-primary/30",
    avatarText: "text-primary font-bold",
    avatarInitials: "SB",
    bubbleBg: "bg-primary/8 border-primary/20",
    labelBg: "bg-primary/15 text-primary",
    senderColor: "text-primary",
  },
  russian: {
    label: "RU Client",
    avatarBg: "bg-indigo-100 border-indigo-300",
    avatarText: "text-indigo-700 font-bold",
    avatarInitials: "RU",
    bubbleBg: "bg-indigo-50 border-indigo-200",
    labelBg: "bg-indigo-100 text-indigo-700",
    senderColor: "text-indigo-700",
  },
  indian: {
    label: "IN Supplier",
    avatarBg: "bg-amber-100 border-amber-300",
    avatarText: "text-amber-700 font-bold",
    avatarInitials: "IN",
    bubbleBg: "bg-amber-50 border-amber-200",
    labelBg: "bg-amber-100 text-amber-700",
    senderColor: "text-amber-700",
  },
  system: {
    label: "AI",
    avatarBg: "bg-primary/15 border-primary/30",
    avatarText: "text-primary",
    avatarInitials: "",
    bubbleBg: "bg-primary/5 border-primary/15",
    labelBg: "bg-primary/10 text-primary",
    senderColor: "text-primary",
  },
};

const ChatMessage = ({ message, index }: ChatMessageProps) => {
  const role = getSenderRole(message.sender, message.type);
  const config = roleConfig[role];
  const isSystem = message.type === "system";
  const isSber = role === "sber";
  const SentimentIcon = sentimentIcons[message.sentiment].icon;
  const sentimentClass = sentimentIcons[message.sentiment].className;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.06 }}
      className={`flex gap-3 ${isSber ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 h-8 w-8 rounded-lg flex items-center justify-center border ${config.avatarBg}`}
      >
        {isSystem ? (
          <Bot className="h-4 w-4 text-primary" />
        ) : (
          <span className={`text-[10px] leading-none ${config.avatarText}`}>
            {config.avatarInitials}
          </span>
        )}
      </div>

      {/* Content */}
      <div className={`flex-1 min-w-0 ${isSber ? "flex flex-col items-end" : ""}`}>
        <div className={`flex items-center gap-2 mb-1 ${isSber ? "flex-row-reverse" : ""}`}>
          <span className={`text-xs font-semibold ${config.senderColor}`}>
            {message.sender}
          </span>
          <span
            className={`text-[9px] font-mono font-semibold uppercase px-1.5 py-0.5 rounded ${config.labelBg}`}
          >
            {config.label}
          </span>
          <span className="text-xs text-muted-foreground font-mono">
            {message.timestamp}
          </span>
          <SentimentIcon className={`h-3 w-3 ${sentimentClass}`} />
        </div>
        <div
          className={`text-sm leading-relaxed rounded-lg p-3 border ${
            isSystem
              ? `${config.bubbleBg} text-foreground font-mono text-xs`
              : `${config.bubbleBg} text-secondary-foreground`
          } ${isSber ? "max-w-[85%]" : ""}`}
        >
          {message.content.split("\n").map((line, i) => (
            <p key={i} className={i > 0 ? "mt-1.5" : ""}>
              {line}
            </p>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

export default ChatMessage;
