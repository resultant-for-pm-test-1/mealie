import { mount, type VueWrapper } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { reactive, ref } from "vue";
import RecipeCard from "./RecipeCard.vue";

vi.mock("~/composables/use-logged-in-state", () => ({
  useLoggedInState: () => ({ isOwnGroup: ref(true) }),
}));

const passthrough = { template: "<div><slot /></div>" };
const wrappers: VueWrapper[] = [];

function mountCard(ingredientCount: number) {
  const wrapper = mount(RecipeCard, {
    props: { name: "Soup", slug: "soup", recipeId: "1", ingredientCount } as Record<string, unknown>,
    global: {
      mocks: { $globals: { icons: {} } },
      stubs: {
        VCard: passthrough,
        VCardTitle: passthrough,
        VCardText: passthrough,
        VCardActions: passthrough,
        VExpandTransition: passthrough,
        VHover: { template: "<div><slot :is-hovering=\"false\" :props=\"{}\" /></div>" },
        RecipeCardImage: true,
        RecipeCardRating: true,
        RecipeFavoriteBadge: true,
        RecipeContextMenu: true,
        RecipeChips: true,
        SafeMarkdown: true,
      },
    },
  });
  wrappers.push(wrapper);
  return wrapper;
}

describe("RecipeCard ingredient count", () => {
  beforeEach(() => {
    vi.stubGlobal("useMealieAuth", () => ({ user: ref({ groupSlug: "family" }) }));
    vi.stubGlobal("useRoute", () => reactive({ path: "/g/family", params: { groupSlug: "family" } }));
  });

  afterEach(() => {
    wrappers.forEach(wrapper => wrapper.unmount());
    wrappers.length = 0;
    vi.unstubAllGlobals();
  });

  test("shows the count when it is greater than zero", () => {
    expect(mountCard(5).text()).toContain("5 ingredients");
  });

  test("uses the singular for one ingredient", () => {
    expect(mountCard(1).text()).toContain("1 ingredient");
  });

  test("shows no count when it is zero", () => {
    expect(mountCard(0).text()).not.toMatch(/ingredient/i);
  });
});
