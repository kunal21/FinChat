import React, { useEffect, useMemo, useState } from 'react';

import { AccountType, HoldingType } from './types';
import { getHoldingsByUser } from '../services/api.tsx';

type HoldingsByAccount = {
  [accountId: number]: HoldingType[];
};

const formatMoney = (value: number | null, code?: string | null) => {
  if (value == null) {
    return '-';
  }
  if (code) {
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: code,
        maximumFractionDigits: 2,
      }).format(value);
    } catch (err) {
      return `$${value.toFixed(2)}`;
    }
  }
  return `$${value.toFixed(2)}`;
};

const formatQuantity = (value: number | null) =>
  value == null ? '-' : value.toLocaleString('en-US', { maximumFractionDigits: 6 });

const Holdings = ({
  accounts,
  userId,
}: {
  accounts: AccountType[];
  userId: number;
}) => {
  const [holdingsByAccount, setHoldingsByAccount] = useState<HoldingsByAccount>({});
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const investmentAccounts = useMemo(
    () => accounts.filter(account => account.type === 'investment'),
    [accounts]
  );

  useEffect(() => {
    let isMounted = true;
    const fetchHoldings = async () => {
      if (!investmentAccounts.length) {
        setHoldingsByAccount({});
        setLoadError(null);
        return;
      }

      setIsLoading(true);
      setLoadError(null);

      try {
        const { data } = await getHoldingsByUser(userId);
        if (!isMounted) {
          return;
        }
        const next: HoldingsByAccount = {};
        (data || []).forEach((holding: HoldingType) => {
          if (!next[holding.account_id]) {
            next[holding.account_id] = [];
          }
          next[holding.account_id].push(holding);
        });
        setHoldingsByAccount(next);
      } catch (err) {
        if (!isMounted) {
          return;
        }
        setLoadError('Unable to load holdings right now.');
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchHoldings();

    return () => {
      isMounted = false;
    };
  }, [investmentAccounts, userId]);

  if (!investmentAccounts.length) {
    return null;
  }

  if (!isLoading && !loadError) {
    const hasHoldings = investmentAccounts.some(account => {
      const holdings = holdingsByAccount[account.id] || [];
      return holdings.length > 0;
    });
    if (!hasHoldings) {
      return null;
    }
  }

  return (
    <div className="holdingsContainer">
      <div className="userDataBox">
        <div className="holdingsList">
          <h4 className="holdingsHeading">Holdings</h4>
          {isLoading && <p>Loading holdings...</p>}
          {loadError && <p>{loadError}</p>}
          {!isLoading && !loadError && (
            <>
              {investmentAccounts.map(account => {
                const holdings = holdingsByAccount[account.id] || [];
                if (!holdings.length) {
                  return null;
                }
                return (
                  <div className="accountHoldings" key={account.id}>
                    <div className="title">
                        {account.name} ••••{account.mask}
                    </div>
                    
                    <table className="holdingsTable">
                      <thead>
                        <tr>
                          <th className="holdingsColName">Name</th>
                          <th className="holdingsColQty">Quantity</th>
                          <th className="holdingsColValue">Value</th>
                        </tr>
                      </thead>
                      <tbody>
                      {holdings.map(holding => (
                      <tr className="holdingRow" key={holding.id}>
                        <td className="holdingName">
                          {holding.ticker_symbol || holding.name || 'Holding'}
                        </td>
                        <td className="holdingQty">
                          {formatQuantity(holding.quantity)}
                        </td>
                        <td className="holdingValue">
                          {formatMoney(
                            holding.institution_value,
                            holding.iso_currency_code
                          )}
                        </td>
                      </tr>
                      ))}
                      </tbody>
                    </table>
                    
                  </div>
                );
              })}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Holdings;
