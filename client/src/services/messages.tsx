import React, {
    createContext,
    useContext,
    useReducer,
    useCallback,
    useRef,
    useMemo,
    Dispatch,
    use,
  } from 'react';
import keyBy from 'lodash/keyBy';
import omitBy from 'lodash/omitBy';
import { v4 as uuid } from 'uuid';

import { MessageType } from '../components/types';
import {
getMessagesByUser as apiGetMessagesByUser,
sendMessage as apiSendMessage,
getMessageByMessageId as apiGetMessageByMessageId,
deleteAllMessagesByUser as apiDeleteAllMessagesByUser,
} from './api.tsx';
  
// State: messages keyed by their ID
interface MessagesState {
    [messageId: number]: MessageType;
}

const initialMessages: MessageType = {
    id: -1,
    user_id: 6,
    text: 'Hello! Ask away any personal finance questions.',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    author: 'bot',
};

const initialState: MessagesState = {[initialMessages.id]: initialMessages};
type MessagesAction =
    | { type: 'SUCCESSFUL_GET'; payload: MessageType[] }
    | { type: 'ADD_MESSAGE'; payload: MessageType }
    | { type: 'DELETE_MESSAGE'; payload: number }
    | { type: 'DELETE_ALL_MESSAGES' };

interface MessagesContextShape extends MessagesState {
    messagesById: MessagesState;
    dispatch: Dispatch<MessagesAction>;
    getMessagesByUser: (userId: number, refresh?: boolean) => Promise<void>;
    sendMessage: (userId: number, text: string) => Promise<void>;
    deleteMessage: (messageId: number) => void;
    getMessageByMessageId: (messageId: number) => MessageType | undefined;
    deleteAllMessagesByUser: (userId: number) => Promise<void>;
}
  
const MessagesContext = createContext<MessagesContextShape>(initialState as MessagesContextShape);
  
export function MessagesProvider(props: any) {
    const [messagesById, dispatch] = useReducer(reducer, initialState);
    const hasRequested = useRef<Record<number, boolean>>({});

    const getMessagesByUser = useCallback(
        async (userId: number, refresh = false) => {
        if (!hasRequested.current[userId] || refresh) {
            hasRequested.current[userId] = true;
            const { data } = await apiGetMessagesByUser(userId);
                dispatch({ type: 'SUCCESSFUL_GET', payload: data });
        }
        },
        []
    );

    const sendMessage = useCallback(
        async (userId: number, text: string) => {
        await apiSendMessage(userId, text);
        },
        []
    );

    const deleteAllMessagesByUser = useCallback(
        async (userId: number) => {
        const { data } = await apiDeleteAllMessagesByUser(userId);
            dispatch({ type: 'DELETE_ALL_MESSAGES'});
        },
        []);

    const deleteMessage = useCallback((messageId: number) => {
        dispatch({ type: 'DELETE_MESSAGE', payload: messageId });
    }, []);

    const getMessageByMessageId = useCallback(
        async (messageId: number) => {
        const { data } = await apiGetMessageByMessageId(messageId);
            dispatch({ type: 'ADD_MESSAGE', payload: data });
        },
        []
    );  

    const value = useMemo(
        () => ({
        messagesById,
        dispatch,
        getMessagesByUser,
        sendMessage,
        deleteMessage,
        getMessageByMessageId,
        deleteAllMessagesByUser
        }),
        [messagesById, getMessagesByUser, sendMessage, deleteMessage, getMessageByMessageId, deleteAllMessagesByUser]
    );

    return <MessagesContext.Provider value={value} {...props} />;
}

function reducer(state: MessagesState, action: MessagesAction): MessagesState {
    switch (action.type) {
        case 'SUCCESSFUL_GET':
            if (!action.payload.length) return state;
            return { ...state, ...keyBy(action.payload, 'id') };
        case 'ADD_MESSAGE':
            return { ...state, [action.payload.id]: action.payload };
        case 'DELETE_MESSAGE':
            return omitBy(state, (msg: MessageType) => msg.id === action.payload);
        case 'DELETE_ALL_MESSAGES':
            return initialState;
        default:
            console.warn('unknown action:', action.type);
            return state;
    }
}

export function useMessages() {
    const context = useContext(MessagesContext);
    if (!context) {
        throw new Error('useMessages must be used within a MessagesProvider');
    }
    return context;
}
  