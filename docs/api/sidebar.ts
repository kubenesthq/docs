import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "api/kubenest-backend-api",
    },
    {
      type: "category",
      label: "Authentication",
      items: [
        {
          type: "doc",
          id: "api/user-login",
          label: "User login",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/user-registration",
          label: "User registration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/refresh-jwt-token",
          label: "Refresh JWT token",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/user-logout",
          label: "User logout",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Clusters",
      items: [
        {
          type: "doc",
          id: "api/register-new-cluster",
          label: "Register new cluster",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/list-all-clusters",
          label: "List all clusters",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-cluster-details",
          label: "Get cluster details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/unregister-cluster",
          label: "Unregister cluster",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/get-helm-install-command",
          label: "Get Helm install command",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Projects",
      items: [
        {
          type: "doc",
          id: "api/create-project",
          label: "Create project",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/list-projects",
          label: "List projects",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-project-details",
          label: "Get project details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/delete-project",
          label: "Delete project",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/list-workloads-in-project",
          label: "List workloads in project",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Workloads",
      items: [
        {
          type: "doc",
          id: "api/deploy-workload",
          label: "Deploy workload",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/list-workloads",
          label: "List workloads",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-workload-details",
          label: "Get workload details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/update-workload",
          label: "Update workload",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "api/delete-workload",
          label: "Delete workload",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/trigger-redeployment",
          label: "Trigger redeployment",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Addons",
      items: [
        {
          type: "doc",
          id: "api/install-addon",
          label: "Install addon",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/list-addons",
          label: "List addons",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-addon-details",
          label: "Get addon details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/uninstall-addon",
          label: "Uninstall addon",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Events",
      items: [
        {
          type: "doc",
          id: "api/server-sent-events-stream",
          label: "Server-Sent Events stream",
          className: "api-method get",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
