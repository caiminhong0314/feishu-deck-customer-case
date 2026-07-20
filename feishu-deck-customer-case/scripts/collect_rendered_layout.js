(() => {
  const rect = (node) => {
    const value = node.getBoundingClientRect();
    return { x: value.x, y: value.y, width: value.width, height: value.height };
  };
  const px = (value) => Number.parseFloat(value || "0");
  const pageRoots = [...document.querySelectorAll("[data-case-page]")];
  return {
    schema_version: 2,
    pages: pageRoots.map((root) => {
      const rootRect = rect(root);
      const style = getComputedStyle(root);
      const title = root.querySelector("[data-case-title]");
      const subtitle = root.querySelector("[data-case-subtitle]");
      const titleRect = title ? rect(title) : null;
      const subtitleRect = subtitle ? rect(subtitle) : null;
      const columnRow = root.querySelector("[data-case-column-row]");
      const peerTitles = [...root.querySelectorAll("[data-case-peer-title]")];
      const titleOffsets = peerTitles.map((node) => rect(node).y);
      const evidence = [...root.querySelectorAll("[data-case-evidence]")].map((node) => {
        const image = node.querySelector("img");
        const nestedCaption = node.querySelector('[data-case-copy-role="caption"]');
        const siblingCaption = node.nextElementSibling?.matches?.('[data-case-copy-role="caption"]')
          ? node.nextElementSibling
          : null;
        const caption = nestedCaption || siblingCaption;
        const evidenceRect = rect(node);
        const sourceRatio = Number(node.dataset.caseSourceRatio || "0");
        const nodeStyle = getComputedStyle(node);
        const imageStyle = image ? getComputedStyle(image) : null;
        const imageRect = image ? rect(image) : null;
        const captionStyle = caption ? getComputedStyle(caption) : null;
        return {
          id: node.dataset.caseEvidence,
          ...evidenceRect,
          sequence: node.dataset.caseEvidenceSequence
            ? Number.parseInt(node.dataset.caseEvidenceSequence, 10)
            : null,
          proof_task: node.dataset.caseProofTask || "",
          display_mode: node.dataset.caseDisplayMode || "contain",
          rendered_fit: imageStyle ? imageStyle.objectFit : nodeStyle.backgroundSize,
          overflow_x: nodeStyle.overflowX,
          overflow_y: nodeStyle.overflowY,
          declared_source_aspect_ratio: sourceRatio || null,
          intrinsic_width_px: image?.naturalWidth || null,
          intrinsic_height_px: image?.naturalHeight || null,
          image_box_width_px: imageRect?.width || null,
          image_box_height_px: imageRect?.height || null,
          caption_mode: node.dataset.caseCaptionMode || "",
          caption_background_color: captionStyle?.backgroundColor || "",
          caption_background_image: captionStyle?.backgroundImage || "",
        };
      });
      const copy = [...root.querySelectorAll("[data-case-copy-role]")].map((node) => {
        const nodeStyle = getComputedStyle(node);
        return {
          role: node.dataset.caseCopyRole,
          font_px: px(nodeStyle.fontSize),
          font_weight: nodeStyle.fontWeight,
          color: nodeStyle.color,
          ...rect(node),
        };
      });
      const metrics = [...root.querySelectorAll("[data-case-metric-id]")].map((node) => {
        const nodeStyle = getComputedStyle(node);
        return {
          id: node.dataset.caseMetricId,
          placement: node.dataset.caseMetricPlacement || "",
          status: node.dataset.caseMetricStatus || "",
          background_image: nodeStyle.backgroundImage,
          border_color: nodeStyle.borderTopColor,
          border_radius_px: px(nodeStyle.borderTopLeftRadius),
          ...rect(node),
        };
      });
      const metricBand = root.querySelector("[data-case-metric-band]");
      const metricBandStyle = metricBand ? getComputedStyle(metricBand) : null;
      const composition = root.querySelector("[data-case-evidence-composition]");
      const painTreatment = root.querySelector("[data-case-pain-treatment]");
      return {
        id: root.dataset.casePage,
        canvas: { width: rootRect.width, height: rootRect.height },
        top_grid: root.querySelector('[data-case-top-grid="true"]') !== null,
        regions: [...root.querySelectorAll("[data-case-region]")].map((node) => ({
          id: node.dataset.caseRegion,
          role: node.dataset.caseRole,
          ...rect(node),
        })),
        tokens: {
          title_px: title ? px(getComputedStyle(title).fontSize) : null,
          subtitle_px: subtitle ? px(getComputedStyle(subtitle).fontSize) : null,
          title_subtitle_gap_px: titleRect && subtitleRect ? subtitleRect.y - (titleRect.y + titleRect.height) : null,
          column_gap_px: columnRow ? px(getComputedStyle(columnRow).columnGap || getComputedStyle(columnRow).gap) : null,
          peer_title_baseline_delta_px: titleOffsets.length > 1 ? Math.max(...titleOffsets) - Math.min(...titleOffsets) : 0,
        },
        blocks: [...root.querySelectorAll("[data-case-block]")].map((node) => ({
          id: node.dataset.caseBlock,
          ...rect(node),
          allow_overlap_with: (node.dataset.caseAllowOverlapWith || "").split(",").filter(Boolean),
        })),
        copy,
        metrics,
        metric_band_recipe: metricBand?.dataset.caseMetricBand || "",
        metric_band: metricBand ? {
          gap_px: px(metricBandStyle.columnGap || metricBandStyle.gap),
          background_image: metricBandStyle.backgroundImage,
          border_width_px: px(metricBandStyle.borderTopWidth),
        } : null,
        evidence,
        evidence_composition: composition ? {
          recipe: composition.dataset.caseEvidenceComposition || "",
          asset_ids_in_visual_order: (composition.dataset.caseEvidenceCompositionAssets || "")
            .split("|")
            .filter(Boolean),
        } : null,
        pain_detail: painTreatment ? {
          recipe: painTreatment.dataset.casePainTreatment || "",
          points: [...painTreatment.querySelectorAll("[data-case-pain-point]")].map((node, index) => {
            const pointStyle = getComputedStyle(node);
            return {
              index: index + 1,
              ...rect(node),
              background_color: pointStyle.backgroundColor,
              background_image: pointStyle.backgroundImage,
              border_width_px: px(pointStyle.borderTopWidth),
              outline_width_px: px(pointStyle.outlineWidth),
              box_shadow: pointStyle.boxShadow,
            };
          }),
        } : null,
        flow: {
          placement: root.querySelector("[data-case-flow]")?.dataset.caseFlowPlacement || "absent",
          container_id: root.querySelector("[data-case-flow]")?.dataset.caseFlowContainer || "",
        },
      };
    }),
  };
})()
