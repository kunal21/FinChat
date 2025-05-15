import React, { useEffect, useRef } from 'react';
import { toast } from 'react-toastify';

import { useAccounts, useItems, useTransactions } from '../services';
import { useMessages } from 'src/services/messages';
const io = require('socket.io-client');
const { REACT_APP_SERVER_PORT } = process.env;

export default function Sockets() {
  const socket = useRef();
  const { getAccountsByItem } = useAccounts();
  const { getTransactionsByItem } = useTransactions();
  const { getItemById } = useItems();
  const { dispatch } = useMessages();

  useEffect(() => {
    socket.current = io(`http://localhost:5001`);

    socket.current.on('SYNC_UPDATES_AVAILABLE', ({ itemId } = {}) => {
      const msg = `New Webhook Event: Item ${itemId}: Transactions updates`;
      console.log(msg);
      toast(msg);
      getAccountsByItem(itemId);
      getTransactionsByItem(itemId);
    });

    socket.current.on('ERROR', ({ itemId, errorCode } = {}) => {
      const msg = `New Webhook Event: Item ${itemId}: Item Error ${errorCode}`;
      console.error(msg);
      toast.error(msg);
      getItemById(itemId, true);
    });

    socket.current.on('PENDING_EXPIRATION', ({ itemId } = {}) => {
      const msg = `New Webhook Event: Item ${itemId}: Access consent is expiring in 7 days. To prevent this, User should re-enter login credentials.`;
      console.log(msg);
      toast(msg);
      getItemById(itemId, true);
    });

    socket.current.on('PENDING_DISCONNECT', ({ itemId } = {}) => {
      const msg = `New Webhook Event: Item ${itemId}: Item will be disconnected in 7 days. To prevent this, User should re-enter login credentials.`;
      console.log(msg);
      toast(msg);
      getItemById(itemId, true);
    });

    socket.current.on('NEW_TRANSACTIONS_DATA', ({ itemId } = {}) => {
      getAccountsByItem(itemId);
      getTransactionsByItem(itemId);
    });

    socket.current.on('NEW_RESPONSE_MESSAGE', ({ message } = {}) => {
      dispatch({
        type: 'ADD_MESSAGE',
        payload: message,
      });
    });

    socket.current.on('DELETE_ALL_MESSAGES', ({} = {}) => {
      dispatch({
        type: 'DELETE_ALL_MESSAGES',
      });
    });

    return () => {
      socket.current.removeAllListeners();
      socket.current.close();
    };
  }, [getAccountsByItem, getTransactionsByItem, getItemById]);

  return <div />;
}
