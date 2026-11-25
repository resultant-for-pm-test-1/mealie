import { mount } from "@vue/test-utils";
import { ref } from "vue";
import { describe, expect, it, vi } from "vitest";
import RecipePageFooter from "./RecipePageFooter.vue";
import type { RecipeOut } from "~/lib/api/types/recipe";

vi.mock("~/composables/recipe-page/shared-state", () => ({
  usePageState: () => ({ isEditForm: ref(false), isCookMode: ref(false) }),
}));

const SITE_NAME_SELECTOR = "[data-testid='recipe-site-name']";

function footer(recipe: Record<string, unknown>) {
  return mount(RecipePageFooter, {
    props: { modelValue: { slug: "test-recipe", extras: {}, ...recipe } as unknown as RecipeOut },
    global: {
      stubs: {
        "v-card-actions": { template: "<div><slot /></div>" },
        "v-btn": { template: "<a><slot /></a>" },
        AdvancedOnly: true,
      },
    },
  });
}

describe("recipe page footer site name", () => {
  it("shows the site name of an imported recipe, including a very long one, in full", () => {
    const wrapper = footer({ orgURL: "https://www.allrecipes.com/recipe/123", siteName: "allrecipes.com" });

    const element = wrapper.find(SITE_NAME_SELECTOR);
    expect(element.exists()).toBe(true);
    expect(element.text()).toContain("allrecipes.com");
    wrapper.unmount();

    const longName = `${"a".repeat(60)}.${"b".repeat(50)}.example.com`;
    const longWrapper = footer({ orgURL: `https://${longName}/recipe`, siteName: longName });

    const longElement = longWrapper.find(SITE_NAME_SELECTOR);
    expect(longElement.exists()).toBe(true);
    expect(longElement.text()).toContain(longName);
    expect(longElement.text()).not.toContain("…");
    expect(longElement.text()).not.toContain("...");
    longWrapper.unmount();
  });

  it("shows no site name for a recipe without one", () => {
    const wrapper = footer({ orgURL: null, siteName: null });

    expect(wrapper.find(SITE_NAME_SELECTOR).exists()).toBe(false);
    expect(wrapper.text()).not.toContain("null");
    wrapper.unmount();
  });
});
