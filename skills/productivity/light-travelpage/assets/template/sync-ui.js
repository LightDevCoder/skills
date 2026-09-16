(() => {
  let refreshing = false;
  const $ = (id) => document.getElementById(id);
  function status(message) {
    $("sync-message").textContent = message;
  }
  window.addEventListener("light:sync-status", (event) => {
    status(event.detail.message);
    $("sync-retry").hidden = !TravelRuntimeStorage.hasPending();
  });
  async function refresh(force = false) {
    if (refreshing || document.hidden || TravelRuntimeStorage.hasPending())
      return;
    if (
      !force &&
      (document.querySelector("dialog[open]") ||
        ["INPUT", "SELECT", "TEXTAREA"].includes(
          document.activeElement?.tagName,
        ))
    )
      return;
    refreshing = true;
    try {
      await window.LightTravelRefresh?.();
      const ledgerRefreshed = await window.TravelLedger?.refresh?.(force);
      if (ledgerRefreshed === false) { status("行程状态已刷新；正在编辑的账本将在完成编辑后同步。"); return; }
      status("已同步 · " + new Date().toLocaleTimeString());
    } catch (error) {
      status(error.message);
    } finally {
      refreshing = false;
    }
  }
  document.addEventListener("DOMContentLoaded", () => {
    $("sync-refresh").onclick = () => refresh(true);
    $("sync-retry").onclick = async () => {
      try {
        const recovered = await TravelRuntimeStorage.retryAll();
        await window.TravelLedger?.recoverSavedMutation?.(recovered);
        $("sync-retry").hidden = !TravelRuntimeStorage.hasPending();
        const failures = recovered.filter(entry => entry.error);
        if (failures.length) { status(failures.map(entry => entry.error.message).join("；")); return; }
        await refresh(true);
      } catch (error) {
        status(error.message);
      }
    };
    $("sync-export").onclick = async () => {
      try {
        const data = await TravelRuntimeStorage.exportSnapshot({
          tripId: TRAVEL_PLAN_DATA.metadata.tripId,
        });
        const url = URL.createObjectURL(
          new Blob([JSON.stringify(data, null, 2)], {
            type: "application/json",
          }),
        );
        const a = document.createElement("a");
        a.href = url;
        a.download = `${data.tripId}-backup.json`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
      } catch (error) {
        status(error.message);
      }
    };
    $("sync-import").onchange = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      try {
        if (file.size > 1500000) throw new Error("备份文件过大");
        const backup = JSON.parse(await file.text());
        const options = { tripId: TRAVEL_PLAN_DATA.metadata.tripId };
        if (
          backup.format !== "light-travelpage-backup-v1" ||
          backup.tripId !== options.tripId
        )
          throw new Error("备份不属于当前旅程");
        const current = await TravelRuntimeStorage.exportSnapshot(options);
        if (
          !confirm(
            `将用备份替换当前共享待办、门票状态和账本（${backup.snapshot?.bills?.length || 0} 笔账单）。建议先导出当前备份。继续恢复？`,
          )
        )
          return;
        await TravelRuntimeStorage.restoreSnapshot(
          options,
          backup,
          current.snapshot.revision,
        );
        await refresh(true);
      } catch (error) {
        status(error.message);
      } finally {
        event.target.value = "";
      }
    };
    window.addEventListener("online", () => refresh());
    window.addEventListener("offline", () =>
      status(
        "网络已断开，当前显示上次读取的内容。未确认保存请恢复网络后重试。",
      ),
    );
    window.addEventListener("focus", () => refresh());
    document.addEventListener("visibilitychange", () => refresh());
    setInterval(() => refresh(), 15000);
  });
})();
