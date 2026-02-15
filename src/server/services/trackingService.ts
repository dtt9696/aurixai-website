/**
 * AURIX 业务事件追踪服务
 * 将后端 API 的业务事件（风险检查、告警、订阅等）上报到仪表盘
 * 
 * 工作原理：
 * 1. 后端 API 在执行业务逻辑时调用此服务
 * 2. 此服务将事件通过 HTTP 发送到仪表盘的 tracking.collect 接口
 * 3. 仪表盘将事件存入数据库，供分析查询使用
 * 
 * 事件先缓存在内存中，定时批量上报，避免影响主业务性能
 */

interface TrackingEvent {
  sessionId: string;
  userId?: string;
  eventType: string;
  eventName: string;
  pagePath?: string;
  metadata?: Record<string, unknown>;
  timestamp: number;
  referrer?: string;
}

class TrackingService {
  private buffer: TrackingEvent[] = [];
  private flushInterval: ReturnType<typeof setInterval> | null = null;
  private dashboardUrl: string;
  private serverSessionId: string;

  /** 上报间隔（毫秒） */
  private readonly FLUSH_INTERVAL = 10000;
  /** 缓冲区最大事件数 */
  private readonly MAX_BUFFER_SIZE = 50;

  constructor() {
    // 仪表盘 URL，从环境变量读取，默认为本地
    this.dashboardUrl =
      process.env.DASHBOARD_URL || "http://localhost:3001";
    this.serverSessionId = `server-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }

  /** 启动定时上报 */
  start() {
    if (this.flushInterval) return;
    this.flushInterval = setInterval(() => this.flush(), this.FLUSH_INTERVAL);
    console.log(
      `📊 [Tracking] 事件追踪服务已启动，上报地址: ${this.dashboardUrl}`
    );
  }

  /** 停止服务 */
  stop() {
    this.flush();
    if (this.flushInterval) {
      clearInterval(this.flushInterval);
      this.flushInterval = null;
    }
  }

  /** 追踪风险检查事件 */
  trackRiskCheck(
    companyId: string,
    companyName: string,
    previousScore: number,
    currentScore: number,
    scoreChange: number
  ) {
    this.addEvent({
      eventType: "risk_check",
      eventName: "risk_check.run",
      metadata: {
        companyId,
        companyName,
        previousScore,
        currentScore,
        scoreChange,
        source: "backend_api",
      },
    });
  }

  /** 追踪 API 调用 */
  trackApiCall(
    apiName: string,
    method: string,
    duration: number,
    success: boolean,
    metadata?: Record<string, unknown>
  ) {
    this.addEvent({
      eventType: "api_call",
      eventName: `api.${apiName}`,
      metadata: {
        method,
        duration,
        success,
        source: "backend_api",
        ...metadata,
      },
    });
  }

  /** 追踪告警发送 */
  trackAlert(
    email: string,
    companyName: string,
    success: boolean,
    scoreChange: number
  ) {
    this.addEvent({
      eventType: "alert",
      eventName: "alert.sent",
      metadata: {
        email,
        companyName,
        success,
        scoreChange,
        source: "backend_api",
      },
    });
  }

  /** 追踪订阅操作 */
  trackSubscription(
    action: "create" | "cancel" | "update",
    companyId: string,
    email: string
  ) {
    this.addEvent({
      eventType: "subscription",
      eventName: `subscription.${action}`,
      metadata: {
        companyId,
        email,
        source: "backend_api",
      },
    });
  }

  /** 追踪定时任务执行 */
  trackCronJob(
    jobName: string,
    duration: number,
    companiesChecked: number,
    notificationsSent: number
  ) {
    this.addEvent({
      eventType: "custom",
      eventName: `cron.${jobName}`,
      metadata: {
        duration,
        companiesChecked,
        notificationsSent,
        source: "cron_job",
      },
    });
  }

  // ===== Private =====

  private addEvent(
    event: Omit<TrackingEvent, "sessionId" | "timestamp">
  ) {
    this.buffer.push({
      ...event,
      sessionId: this.serverSessionId,
      userId: "system",
      timestamp: Date.now(),
    });

    if (this.buffer.length >= this.MAX_BUFFER_SIZE) {
      this.flush();
    }
  }

  private async flush() {
    if (this.buffer.length === 0) return;

    const events = [...this.buffer];
    this.buffer = [];

    try {
      const response = await fetch(
        `${this.dashboardUrl}/api/trpc/tracking.collect`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            json: {
              events,
              session: {
                sessionId: this.serverSessionId,
                userId: "system",
                startedAt: Date.now() - this.FLUSH_INTERVAL,
                endedAt: Date.now(),
                duration: Math.round(this.FLUSH_INTERVAL / 1000),
                pageViews: 0,
                eventCount: events.length,
                isBounce: false,
              },
            },
          }),
          signal: AbortSignal.timeout(5000),
        }
      );

      if (response.ok) {
        console.log(
          `📊 [Tracking] 成功上报 ${events.length} 个事件到仪表盘`
        );
      } else {
        // 上报失败，放回缓冲区
        this.buffer.unshift(...events);
        console.warn(
          `📊 [Tracking] 上报失败 (HTTP ${response.status})，${events.length} 个事件将在下次重试`
        );
      }
    } catch (err) {
      // 网络错误，放回缓冲区（但限制最大缓冲量避免内存泄漏）
      if (this.buffer.length < 500) {
        this.buffer.unshift(...events);
      }
      // 静默处理，不影响主业务
    }
  }
}

/** 全局单例 */
export const trackingService = new TrackingService();
