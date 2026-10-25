export interface WebsocketTicket {
    ticket: string;
}

export interface Conversation {
    id: string;
    party: string;
    read?: string;
    messages?: SMSMessage[];
    unreadCount: number;
    lastMessage: string;
}

export interface ConversationResponse {
    conversations: Conversation[];
}

export interface SMSMessage {
    id?: string;
    conversationId: string;
    timestamp: string;
    message: string;
    inbound: boolean;
}

export interface MessageListResponse {
    messages: SMSMessage[];
}

export enum EventType {
    NEW = 'new',
    UPD = 'upd',
    DEL = 'del'
}

export enum ObjectType {
    CON = 'conversation',
    MES = 'message'
}

export interface MessageEvent {
    event: EventType;
    objectType: ObjectType;
    objectId: string;
    instance?: SMSMessage | Conversation;
}