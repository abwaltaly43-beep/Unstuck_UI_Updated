import React, { useState, useEffect } from 'react';
import { API_BASE } from '../../config/api';
import {
  Trophy,
  Award,
  Sparkles,
  TrendingUp,
  User,
  Briefcase,
  CheckCircle2,
  Filter,
  ArrowRight,
  Flame,
  ShieldCheck,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

export function LeaderboardPage({ userProfile, onNavigate, onToast }) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState('all');
  const [userRankInfo, setUserRankInfo] = useState({
    rank: null,
    total_users: 0,
    total_score: 0,
    skills_score: 0,
    applied_score: 0,
    badge: '🌱 مستخدم جديد',
    percentile: 0,
    is_ranked: false
  });

  // Fetch live leaderboard from FastAPI / Supabase (Strictly real users with total_score > 0)
  const fetchLeaderboardData = async () => {
    setIsLoading(true);
    try {
      const email = userProfile?.email;
      const promises = [fetch(`${API_BASE}/api/leaderboard?limit=50`)];
      if (email) {
        promises.push(fetch(`${API_BASE}/api/user/rank?email=${encodeURIComponent(email)}`));
      }

      const [lbRes, rankRes] = await Promise.all(promises);

      if (lbRes && lbRes.ok) {
        const lbData = await lbRes.json();
        const list = Array.isArray(lbData?.leaderboard) ? lbData.leaderboard : [];
        // Only keep users with score > 0
        setLeaderboard(list.filter(u => (u.total_score || 0) > 0));
      } else {
        setLeaderboard([]);
      }

      if (rankRes && rankRes.ok) {
        const rankData = await rankRes.json();
        if (rankData?.rank_info) {
          setUserRankInfo(rankData.rank_info);
        }
      } else {
        setUserRankInfo({
          rank: null,
          total_users: 0,
          total_score: 0,
          skills_score: 0,
          applied_score: 0,
          badge: '🌱 مستخدم جديد',
          percentile: 0,
          is_ranked: false
        });
      }
    } catch (err) {
      console.warn('Backend leaderboard fetch notice:', err);
      // Clean empty list - strictly NO fake mock data!
      setLeaderboard([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboardData();
  }, [userProfile?.email]);

  // Filtered leaderboard
  const filteredUsers = leaderboard.filter((u) => {
    if (filterCategory === 'all') return true;
    const skillsText = (Array.isArray(u.skills) ? u.skills.join(' ') : String(u.skills || '')).toLowerCase();
    const titleText = (u.title || '').toLowerCase();
    const combined = skillsText + ' ' + titleText;

    if (filterCategory === 'dev') return combined.includes('react') || combined.includes('python') || combined.includes('code') || combined.includes('developer');
    if (filterCategory === 'design') return combined.includes('ui') || combined.includes('ux') || combined.includes('figma') || combined.includes('design');
    if (filterCategory === 'automation') return combined.includes('n8n') || combined.includes('automation') || combined.includes('ai') || combined.includes('scraper');
    return true;
  });

  const top3 = leaderboard.slice(0, 3);
  const isUserRanked = Boolean(userRankInfo?.is_ranked && userRankInfo?.rank && (userRankInfo?.total_score || 0) > 0);

  return (
    <div className="dna-clean-page leaderboard-page-container" style={{ maxWidth: '1000px', margin: '0 auto', padding: '24px 16px' }}>
      {/* 1. Page Header */}
      <div className="clean-page-header" style={{ marginBottom: '24px', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#fef2f2', color: '#be123c', padding: '6px 14px', borderRadius: '999px', fontSize: '13px', fontWeight: '700', marginBottom: '12px' }}>
          <Trophy size={16} />
          <span>لوحة صدارة المستقلين والمبدعين • Application Leaderboard</span>
        </div>
        <h1 className="clean-page-title" style={{ fontSize: '28px', color: '#0f172a' }}>
          ترتيب المستقلين الحقيقي على مستوى التطبيق
        </h1>
        <p className="clean-page-subtitle" style={{ maxWidth: '640px', margin: '8px auto 0', color: '#64748b' }}>
          يتم احتساب الترتيب والنقاط تلقائياً بناءً على المهارات المستخرجة من الـ CV وعدد طلبات التقديم ومقترحات المشاريع. لا تظهر الحسابات ذات النقاط الصفرية.
        </p>
      </div>

      {/* 2. Current User Personal Rank Card */}
      <div style={{
        background: isUserRanked
          ? 'linear-gradient(135deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%)'
          : 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        borderRadius: '16px',
        padding: '24px',
        color: '#ffffff',
        marginBottom: '28px',
        boxShadow: '0 8px 24px rgba(15, 23, 42, 0.15)',
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '16px',
            background: 'rgba(255, 255, 255, 0.12)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            border: '2px solid rgba(255, 255, 255, 0.25)'
          }}>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', opacity: 0.8 }}>Rank</span>
            <span style={{ fontSize: isUserRanked ? '24px' : '18px', fontWeight: '900', color: isUserRanked ? '#fef08a' : '#94a3b8' }}>
              {isUserRanked ? `#${userRankInfo.rank}` : '-'}
            </span>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <h2 style={{ margin: 0, fontSize: '20px', fontWeight: '800' }}>
                {userProfile?.name || 'مستقل'}
              </h2>
              <span style={{
                background: isUserRanked ? '#fef08a' : 'rgba(255, 255, 255, 0.15)',
                color: isUserRanked ? '#854d0e' : '#e2e8f0',
                padding: '3px 10px',
                borderRadius: '999px',
                fontSize: '11.5px',
                fontWeight: '800'
              }}>
                {isUserRanked ? userRankInfo.badge : '🌱 غير مصنف بعد (0 نقطة)'}
              </span>
            </div>
            <p style={{ margin: 0, fontSize: '13px', opacity: 0.85 }}>
              {userProfile?.title || 'مستقل مسجل'}
            </p>
            <div style={{ marginTop: '8px', fontSize: '12px', color: isUserRanked ? '#c7d2fe' : '#cbd5e1' }}>
              {isUserRanked ? (
                <>🎯 أنت متقدم على <strong>{userRankInfo.percentile || 0}%</strong> من المستقلين المسجلين في التطبيق!</>
              ) : (
                <>💡 لم تدخل التصنيف بعد. ارفع سيرتك الذاتية (CV) واستخرج مهاراتك لبدء كسب النقاط ودخول لوحة الصدارة!</>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.1)', padding: '12px 18px', borderRadius: '12px', textAlign: 'center', minWidth: '90px' }}>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>مجموع النقاط</div>
            <div style={{ fontSize: '20px', fontWeight: '900', color: isUserRanked ? '#fde047' : '#ffffff' }}>
              {userRankInfo.total_score || 0}
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.1)', padding: '12px 18px', borderRadius: '12px', textAlign: 'center', minWidth: '90px' }}>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>نقاط المهارات (CV)</div>
            <div style={{ fontSize: '18px', fontWeight: '800' }}>
              +{userRankInfo.skills_score || 0}
            </div>
          </div>
          <div style={{ background: 'rgba(255, 255, 255, 0.1)', padding: '12px 18px', borderRadius: '12px', textAlign: 'center', minWidth: '90px' }}>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>الشغل والمقترحات</div>
            <div style={{ fontSize: '18px', fontWeight: '800' }}>
              +{userRankInfo.applied_score || 0}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Top Podium (Visible when ranked users exist) */}
      {top3.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: top3.length === 1 ? '1fr' : top3.length === 2 ? 'repeat(2, 1fr)' : 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '16px',
          marginBottom: '28px'
        }}>
          {/* Rank 2 (if exists) */}
          {top3[1] && (
            <div style={{
              background: '#ffffff',
              borderRadius: '14px',
              padding: '20px',
              border: '1px solid #e2e8f0',
              textAlign: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
            }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🥈</div>
              <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '700' }}>RANK #2</div>
              <div style={{ fontSize: '16px', fontWeight: '800', color: '#0f172a', margin: '4px 0' }}>{top3[1]?.full_name}</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '10px' }}>{top3[1]?.title || 'مستقل'}</div>
              <span style={{ background: '#f1f5f9', color: '#334155', padding: '4px 12px', borderRadius: '999px', fontSize: '13px', fontWeight: '800' }}>
                {top3[1]?.total_score} pts
              </span>
            </div>
          )}

          {/* Rank 1 (Gold) */}
          {top3[0] && (
            <div style={{
              background: 'linear-gradient(180deg, #fffbeb 0%, #ffffff 100%)',
              borderRadius: '16px',
              padding: '24px 20px',
              border: '2px solid #f59e0b',
              textAlign: 'center',
              boxShadow: '0 6px 20px rgba(245, 158, 11, 0.15)',
              transform: 'translateY(-4px)'
            }}>
              <div style={{ fontSize: '40px', marginBottom: '6px' }}>👑 🥇</div>
              <div style={{ fontSize: '12px', color: '#b45309', fontWeight: '800' }}>TOP PERFORMER • #1</div>
              <div style={{ fontSize: '18px', fontWeight: '900', color: '#0f172a', margin: '4px 0' }}>{top3[0]?.full_name}</div>
              <div style={{ fontSize: '12.5px', color: '#64748b', marginBottom: '12px' }}>{top3[0]?.title || 'مستقل'}</div>
              <span style={{ background: '#f59e0b', color: '#ffffff', padding: '6px 16px', borderRadius: '999px', fontSize: '14px', fontWeight: '900' }}>
                {top3[0]?.total_score} pts • {top3[0]?.badge || '🏆 المتصدر'}
              </span>
            </div>
          )}

          {/* Rank 3 (if exists) */}
          {top3[2] && (
            <div style={{
              background: '#ffffff',
              borderRadius: '14px',
              padding: '20px',
              border: '1px solid #e2e8f0',
              textAlign: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
            }}>
              <div style={{ fontSize: '32px', marginBottom: '8px' }}>🥉</div>
              <div style={{ fontSize: '12px', color: '#64748b', fontWeight: '700' }}>RANK #3</div>
              <div style={{ fontSize: '16px', fontWeight: '800', color: '#0f172a', margin: '4px 0' }}>{top3[2]?.full_name}</div>
              <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '10px' }}>{top3[2]?.title || 'مستقل'}</div>
              <span style={{ background: '#f1f5f9', color: '#334155', padding: '4px 12px', borderRadius: '999px', fontSize: '13px', fontWeight: '800' }}>
                {top3[2]?.total_score} pts
              </span>
            </div>
          )}
        </div>
      )}

      {/* 4. Filter Tabs & Refresh */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {[
            { id: 'all', label: 'الكل (All)' },
            { id: 'dev', label: 'برمجة وتطوير' },
            { id: 'automation', label: 'ذكاء وأتمتة (AI)' },
            { id: 'design', label: 'تصميم UI/UX' }
          ].map(tab => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setFilterCategory(tab.id)}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                fontSize: '13px',
                fontWeight: '600',
                border: filterCategory === tab.id ? '1px solid #be123c' : '1px solid #e2e8f0',
                background: filterCategory === tab.id ? '#be123c' : '#ffffff',
                color: filterCategory === tab.id ? '#ffffff' : '#475569',
                cursor: 'pointer'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={fetchLeaderboardData}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#f8fafc',
            border: '1px solid #e2e8f0',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '12px',
            color: '#475569',
            cursor: 'pointer'
          }}
        >
          <RefreshCw size={13} className={isLoading ? 'animate-spin' : ''} />
          <span>تحديث الترتيب اللحظي</span>
        </button>
      </div>

      {/* 5. Full Leaderboard Table or Clean Empty State */}
      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '48px 16px', color: '#64748b' }}>
          <RefreshCw size={28} className="animate-spin" style={{ margin: '0 auto 12px', display: 'block' }} />
          <p style={{ margin: 0, fontSize: '14px' }}>جاري تحميل لوحة الصدارة الحقيقية...</p>
        </div>
      ) : filteredUsers.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '48px 24px',
          background: '#ffffff',
          borderRadius: '16px',
          border: '1px dashed #cbd5e1',
          margin: '16px 0',
          boxShadow: '0 2px 8px rgba(0,0,0,0.02)'
        }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: '#fef2f2',
            color: '#be123c',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <Trophy size={28} />
          </div>
          <h3 style={{ fontSize: '18px', color: '#0f172a', fontWeight: '800', marginBottom: '8px' }}>
            لا يوجد متصدرين في هذا التصنيف حالياً
          </h3>
          <p style={{ fontSize: '13.5px', color: '#64748b', maxWidth: '460px', margin: '0 auto 20px', lineHeight: 1.6 }}>
            لوحة الصدارة تعرض حصرياً المستخدمين الحقيقيين الحاصلين على نقاط (&gt; 0). ارفع سيرتك الذاتية وقدّم مقترحك لتكون في صدارة القائمة!
          </p>
          <button
            type="button"
            onClick={() => onNavigate('freelance-dna')}
            style={{
              background: '#be123c',
              color: '#ffffff',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '10px',
              fontWeight: '700',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>استخراج المهارات واحتساب النقاط</span>
            <ArrowRight size={15} />
          </button>
        </div>
      ) : (
        <div style={{ background: '#ffffff', borderRadius: '16px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 4px 16px rgba(0,0,0,0.03)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'right' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0', color: '#64748b', fontSize: '12px' }}>
                <th style={{ padding: '14px 16px', textAlign: 'center', width: '70px' }}>الترتيب</th>
                <th style={{ padding: '14px 16px' }}>المستقل / التخصص</th>
                <th style={{ padding: '14px 16px' }}>المهارات المثبتة (CV)</th>
                <th style={{ padding: '14px 16px', textAlign: 'center' }}>الشغل المطبق</th>
                <th style={{ padding: '14px 16px', textAlign: 'center' }}>الرتبة</th>
                <th style={{ padding: '14px 16px', textAlign: 'center' }}>النقاط</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user, idx) => {
                const isCurrentUser = Boolean(userProfile?.email && user.email === userProfile.email);
                const skillsList = Array.isArray(user.skills) ? user.skills : [];
                return (
                  <tr
                    key={user.email || idx}
                    style={{
                      borderBottom: '1px solid #f1f5f9',
                      background: isCurrentUser ? '#fff1f2' : (idx % 2 === 0 ? '#ffffff' : '#fafafa'),
                      transition: 'background 0.15s ease'
                    }}
                  >
                    {/* Rank */}
                    <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                      {idx === 0 ? (
                        <span style={{ fontSize: '18px' }}>🥇</span>
                      ) : idx === 1 ? (
                        <span style={{ fontSize: '18px' }}>🥈</span>
                      ) : idx === 2 ? (
                        <span style={{ fontSize: '18px' }}>🥉</span>
                      ) : (
                        <span style={{ fontWeight: '700', color: '#64748b', fontSize: '14px' }}>#{idx + 1}</span>
                      )}
                    </td>

                    {/* Name & Title */}
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: '800', color: '#0f172a', fontSize: '14px' }}>
                          {user.full_name || 'مستقل'}
                        </span>
                        {isCurrentUser && (
                          <span style={{ background: '#be123c', color: '#ffffff', fontSize: '10.5px', padding: '2px 8px', borderRadius: '999px', fontWeight: '700' }}>
                            أنت (You)
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                        {user.title || 'مستقل'}
                      </div>
                    </td>

                    {/* Skills */}
                    <td style={{ padding: '14px 16px' }}>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                        {skillsList.slice(0, 4).map((s) => (
                          <span
                            key={s}
                            style={{
                              background: '#f1f5f9',
                              color: '#334155',
                              padding: '2px 8px',
                              borderRadius: '6px',
                              fontSize: '11px',
                              fontWeight: '600'
                            }}
                          >
                            {s}
                          </span>
                        ))}
                        {skillsList.length > 4 && (
                          <span style={{ fontSize: '11px', color: '#94a3b8', alignSelf: 'center' }}>
                            +{skillsList.length - 4}
                          </span>
                        )}
                        {skillsList.length === 0 && (
                          <span style={{ fontSize: '11px', color: '#94a3b8' }}>-</span>
                        )}
                      </div>
                    </td>

                    {/* Applied Work */}
                    <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                      <div style={{ fontSize: '13px', fontWeight: '700', color: '#0f172a' }}>
                        {(user.applied_jobs_count || 0) + (user.proposals_count || 0)} عمل
                      </div>
                      <div style={{ fontSize: '11px', color: '#94a3b8' }}>
                        {user.applied_jobs_count || 0} تقديم • {user.proposals_count || 0} مقترح
                      </div>
                    </td>

                    {/* Badge */}
                    <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                      <span style={{
                        background: '#fef2f2',
                        color: '#991b1b',
                        border: '1px solid #fee2e2',
                        padding: '3px 10px',
                        borderRadius: '999px',
                        fontSize: '11px',
                        fontWeight: '700',
                        whiteSpace: 'nowrap'
                      }}>
                        {user.badge || '🌱 مستخدم نشط'}
                      </span>
                    </td>

                    {/* Points */}
                    <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                      <span style={{ fontSize: '15px', fontWeight: '900', color: '#be123c' }}>
                        {user.total_score || 0}
                      </span>
                      <span style={{ fontSize: '11px', color: '#94a3b8', display: 'block' }}>pts</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* 6. How to Boost Rank Card */}
      <div style={{
        marginTop: '28px',
        background: '#f8fafc',
        borderRadius: '14px',
        padding: '20px',
        border: '1px solid #e2e8f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '16px'
      }}>
        <div>
          <h3 style={{ margin: '0 0 4px 0', fontSize: '15px', color: '#0f172a', fontWeight: '800' }}>
            🚀 كيف ترفع ترتيبك في صدارة Unstuck؟
          </h3>
          <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>
            1. ارفع سيرتك الذاتية (CV) لاستخراج وتأكيد كافة مهاراتك (+25 نقطة لكل مهارة مطلوبة).<br />
            2. ولّد مقترحات ذكية وقدّم على الفرص المتطابقة مع رادارك (+50 نقطة لكل تقديم).
          </p>
        </div>
        <button
          type="button"
          onClick={() => onNavigate('freelance-dna')}
          style={{
            background: '#be123c',
            color: '#ffffff',
            border: 'none',
            padding: '10px 20px',
            borderRadius: '10px',
            fontWeight: '700',
            fontSize: '13px',
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span>تحديث الـ CV والمهارات الآن</span>
          <ArrowRight size={15} />
        </button>
      </div>
    </div>
  );
}

export default LeaderboardPage;
