import { useEffect, useState } from 'react';
import Button from 'plaid-threads/Button';

import { getUserImpacts, updateUserImpact } from '../services/api';

type UserImpact = {
  id: string;
  ticker: string;
  impact_level: 'HIGH' | 'MEDIUM' | 'LOW';
  impact_summary: string;
  estimated_effect: string | null;
  read: boolean;
  dismissed: boolean;
  created_at: string;
  article: {
    id: string;
    title: string;
    summary: string;
    url: string;
    source: string;
    published_at: string;
  } | null;
};

type ImpactCard = {
  id: string;
  ticker: string;
  impactLevel: 'High' | 'Medium' | 'Low';
  whatHappened: string;
  whyItMatters: string;
  estimatedImpact: string;
  articleUrl?: string;
  source?: string;
};

const impactClassName = (level: ImpactCard['impactLevel']) => {
  if (level === 'High') return 'impactLevel impactLevel--high';
  if (level === 'Medium') return 'impactLevel impactLevel--medium';
  return 'impactLevel impactLevel--low';
};

const formatImpactLevel = (level: string): 'High' | 'Medium' | 'Low' => {
  if (level === 'HIGH') return 'High';
  if (level === 'MEDIUM') return 'Medium';
  return 'Low';
};

const transformUserImpact = (impact: UserImpact): ImpactCard => {
  return {
    id: impact.id,
    ticker: impact.ticker,
    impactLevel: formatImpactLevel(impact.impact_level),
    whatHappened: impact.article?.title || 'News article',
    whyItMatters: impact.impact_summary,
    estimatedImpact: impact.estimated_effect
      ? `Estimated effect: ${impact.estimated_effect}`
      : 'Impact being assessed',
    articleUrl: impact.article?.url,
    source: impact.article?.source,
  };
};

interface PortfolioImpactProps {
  userId: number;
}

const PortfolioImpact = ({ userId }: PortfolioImpactProps) => {
  const [impacts, setImpacts] = useState<UserImpact[]>([]);
  const [loading, setLoading] = useState(true);
  const [uniqueTickers, setUniqueTickers] = useState<number>(0);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    if (userId) {
      fetchImpacts();
    }
  }, [userId]);

  const fetchImpacts = async () => {
    try {
      setLoading(true);
      const response = await getUserImpacts(userId);
      const impactsData = response.data || [];
      setImpacts(impactsData);

      // Calculate unique tickers
      const tickers = new Set(impactsData.map((i: UserImpact) => i.ticker));
      setUniqueTickers(tickers.size);

      // Set last updated time
      if (impactsData.length > 0) {
        const mostRecent = new Date(impactsData[0].created_at);
        const now = new Date();
        const diffMinutes = Math.floor(
          (now.getTime() - mostRecent.getTime()) / 60000
        );

        if (diffMinutes < 1) {
          setLastUpdated('Just now');
        } else if (diffMinutes < 60) {
          setLastUpdated(`${diffMinutes}m ago`);
        } else if (diffMinutes < 1440) {
          setLastUpdated(`${Math.floor(diffMinutes / 60)}h ago`);
        } else {
          setLastUpdated(`${Math.floor(diffMinutes / 1440)}d ago`);
        }
      } else {
        setLastUpdated('No updates');
      }
    } catch (error) {
      console.error('Error fetching impacts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = async (impactId: string) => {
    try {
      await updateUserImpact(userId, impactId, { dismissed: true });
      // Remove from UI
      setImpacts(impacts.filter(i => i.id !== impactId));
    } catch (error) {
      console.error('Error dismissing impact:', error);
    }
  };

  const handleMarkRead = async (impactId: string) => {
    try {
      await updateUserImpact(userId, impactId, { read: true });
      // Update local state
      setImpacts(
        impacts.map(i => (i.id === impactId ? { ...i, read: true } : i))
      );
    } catch (error) {
      console.error('Error marking impact as read:', error);
    }
  };

  const activeImpacts = impacts.filter(i => !i.dismissed);
  const cards = activeImpacts.map(transformUserImpact);

  if (loading) {
    return (
      <div className="portfolioImpactPage">
        <div className="portfolioHero">
          <p className="portfolioKicker">Portfolio Impact</p>
          <h1>Loading your portfolio impacts...</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="portfolioImpactPage">
      <div className="portfolioHero">
        <div>
          <p className="portfolioKicker">Portfolio Impact</p>
          <h1>News-driven risk map for your holdings</h1>
          <p className="portfolioSubhead">
            Each card links breaking headlines to your exposure so you can
            decide what to do next.
          </p>
        </div>
        <div className="portfolioHeroMeta">
          <div>
            <div className="metaLabel">Active alerts</div>
            <div className="metaValue">{activeImpacts.length}</div>
          </div>
          <div>
            <div className="metaLabel">Coverage</div>
            <div className="metaValue">{uniqueTickers} tickers</div>
          </div>
          <div>
            <div className="metaLabel">Updated</div>
            <div className="metaValue">{lastUpdated}</div>
          </div>
        </div>
      </div>

      {cards.length === 0 ? (
        <div className="impactGrid">
          <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
            No portfolio impacts at this time. Check back later for news about
            your holdings.
          </div>
        </div>
      ) : (
        <div className="impactGrid">
          {cards.map(card => (
            <div className="impactCard" key={card.id}>
              <div className="impactHeader">
                <div className="impactTicker">{card.ticker}</div>
                <div className={impactClassName(card.impactLevel)}>
                  {card.impactLevel} impact
                </div>
              </div>

              <div className="impactSection">
                <div className="impactLabel">What happened</div>
                <p>{card.whatHappened}</p>
                {card.source && (
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.25rem' }}>
                    Source: {card.source}
                  </p>
                )}
              </div>

              <div className="impactSection">
                <div className="impactLabel">Why it affects you</div>
                <p>{card.whyItMatters}</p>
              </div>

              <div className="impactSection">
                <div className="impactLabel">Estimated impact</div>
                <p className="impactEstimate">{card.estimatedImpact}</p>
              </div>

              <div className="impactActions">
                {card.articleUrl && (
                  <Button
                    inline
                    onClick={() => window.open(card.articleUrl, '_blank')}
                  >
                    Read full article
                  </Button>
                )}
                <Button inline secondary>
                  Ask FinChat
                </Button>
                <Button
                  inline
                  className="impactGhost"
                  onClick={() => handleMarkRead(card.id)}
                >
                  Mark read
                </Button>
                <Button
                  inline
                  className="impactGhost"
                  onClick={() => handleDismiss(card.id)}
                >
                  Dismiss
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PortfolioImpact;
